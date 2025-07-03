# logica_recursos/lambdas/startTranscoding/main.py
import json
import os
import boto3

def handler(event, context):
    """
    Starts a MediaConvert job when a video is uploaded to the original S3 bucket.
    """
    print(f"Request received: {event}")

    # Variables de entorno
    transcoded_bucket_name = os.environ.get('TRANSCODED_VIDEOS_BUCKET_NAME')
    mediaconvert_role_arn = os.environ.get('MEDIACONVERT_ROLE_ARN')

    try:
        # 1. Descubrir el endpoint de MediaConvert
        # Es una buena práctica no hardcodearlo.
        mc_client_discovery = boto3.client('mediaconvert')
        response = mc_client_discovery.describe_endpoints()
        mediaconvert_endpoint = response['Endpoints'][0]['Url']
        
        # 2. Crear el cliente de MediaConvert con el endpoint correcto
        mediaconvert_client = boto3.client('mediaconvert', endpoint_url=mediaconvert_endpoint)

        # 3. Extraer información del evento de S3
        s3_event = event['Records'][0]['s3']
        original_bucket = s3_event['bucket']['name']
        object_key = s3_event['object']['key']
        
        source_s3 = f"s3://{original_bucket}/{object_key}"
        # Quitar la extensión del archivo original para el nombre de salida
        output_key = os.path.splitext(object_key)[0]
        destination_s3 = f"s3://{transcoded_bucket_name}/{output_key}/"

        # 4. Definir la configuración del trabajo de MediaConvert
        # (El resto del código permanece igual)
        settings = {
            "OutputGroups": [
                {
                    "Name": "File Group",
                    "OutputGroupSettings": {
                        "Type": "FILE_GROUP_SETTINGS",
                        "FileGroupSettings": {
                            "Destination": destination_s3
                        }
                    },
                    "Outputs": [
                        {
                            "VideoDescription": {
                                "ScalingBehavior": "DEFAULT",
                                "TimecodeInsertion": "DISABLED",
                                "AntiAlias": "ENABLED",
                                "Sharpness": 50,
                                "CodecSettings": {
                                    "Codec": "H_264",
                                    "H264Settings": {
                                        "InterlaceMode": "PROGRESSIVE",
                                        "NumberReferenceFrames": 3,
                                        "Syntax": "DEFAULT",
                                        "Softness": 0,
                                        "GopClosedCadence": 1,
                                        "GopSize": 90,
                                        "Slices": 1,
                                        "GopBReference": "DISABLED",
                                        "SlowPal": "DISABLED",
                                        "SpatialAdaptiveQuantization": "ENABLED",
                                        "TemporalAdaptiveQuantization": "ENABLED",
                                        "FlickerAdaptiveQuantization": "DISABLED",
                                        "EntropyEncoding": "CABAC",
                                        "Bitrate": 5000000,
                                        "RateControlMode": "CBR",
                                        "CodecProfile": "MAIN",
                                        "Telecine": "NONE",
                                        "MinIInterval": 0,
                                        "AdaptiveQuantization": "HIGH",
                                        "CodecLevel": "AUTO",
                                        "FieldEncoding": "PAFF",
                                        "SceneChangeDetect": "ENABLED",
                                        "QualityTuningLevel": "SINGLE_PASS",
                                        "FramerateControl": "INITIALIZE_FROM_SOURCE",
                                        "GopSizeUnits": "FRAMES",
                                        "ParControl": "INITIALIZE_FROM_SOURCE",
                                        "NumberBFramesBetweenReferenceFrames": 2,
                                        "RepeatPps": "DISABLED",
                                        "DynamicSubGop": "STATIC"
                                    }
                                }
                            },
                            "AudioDescriptions": [
                                {
                                    "AudioTypeControl": "FOLLOW_INPUT",
                                    "CodecSettings": {
                                        "Codec": "AAC",
                                        "AacSettings": {
                                            "AudioDescriptionBroadcasterMix": "NORMAL",
                                            "Bitrate": 96000,
                                            "RateControlMode": "CBR",
                                            "CodecProfile": "LC",
                                            "CodingMode": "CODING_MODE_2_0",
                                            "RawFormat": "NONE",
                                            "SampleRate": 48000,
                                            "Specification": "MPEG4"
                                        }
                                    }
                                }
                            ],
                            "ContainerSettings": {
                                "Container": "MP4",
                                "Mp4Settings": {}
                            }
                        }
                    ]
                }
            ],
            "Inputs": [
                {
                    "AudioSelectors": {
                        "Audio Selector 1": {
                            "Offset": 0,
                            "DefaultSelection": "DEFAULT",
                            "ProgramSelection": 1
                        }
                    },
                    "VideoSelector": {
                        "ColorSpace": "FOLLOW"
                    },
                    "FilterEnable": "AUTO",
                    "PsiControl": "USE_PSI",
                    "FilterStrength": 0,
                    "DeblockFilter": "DISABLED",
                    "DenoiseFilter": "DISABLED",
                    "TimecodeSource": "EMBEDDED",
                    "FileInput": source_s3
                }
            ]
        }

        # 5. Crear el trabajo
        print(f"Starting MediaConvert job for {source_s3}")
        mediaconvert_client.create_job(
            Role=mediaconvert_role_arn,
            Settings=settings,
            UserMetadata={
                'sourceObjectKey': object_key
            }
        )
        print("Successfully started MediaConvert job.")

        return {
            'statusCode': 200,
            'body': json.dumps('Transcoding job started successfully!')
        }

    except Exception as e:
        print(f"Error starting MediaConvert job: {e}")
        raise e
