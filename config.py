import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações da AWS
AWS_REGION = os.getenv('AWS_REGION', 'sa-east-1')

# Configurações da instância EC2
INSTANCE_ID = os.getenv('INSTANCE_ID', 'i-05249f744fa92653c')
INSTANCE_TYPE = 't2.micro'
AMI_ID = 'ami-0c7217cdde317cfec'  # Ubuntu 22.04 LTS
KEY_PAIR_NAME = os.getenv('KEY_PAIR_NAME', 'MyInstance')  # Nome do par de chaves atualizado
SECURITY_GROUP_NAME = 'ec2-security-group'

# Tags padrão para as instâncias
DEFAULT_TAGS = [
    {
        'Key': 'Name',
        'Value': 'ec2-instance'
    },
    {
        'Key': 'Environment',
        'Value': 'development'
    }
] 