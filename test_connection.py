import boto3
from botocore.exceptions import ClientError
from config import AWS_REGION, INSTANCE_ID, KEY_PAIR_NAME
from ec2_manager import EC2Manager
import json
from datetime import datetime
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

def format_timestamp(timestamp):
    """Formata o timestamp para exibição."""
    return datetime.fromisoformat(timestamp).strftime('%d/%m/%Y %H:%M:%S')

def test_aws_connection():
    """Testa a conexão com AWS e exibe informações da instância."""
    try:
        print("\n=== Testando Conexão com AWS ===")
        print("=" * 50)
        
        # Verifica se as credenciais AWS estão configuradas
        if not os.getenv('AWS_ACCESS_KEY_ID') or not os.getenv('AWS_SECRET_ACCESS_KEY'):
            print("\n❌ Erro: Credenciais AWS não encontradas!")
            print("Por favor, configure as seguintes variáveis no arquivo .env:")
            print("AWS_ACCESS_KEY_ID=sua_access_key_aqui")
            print("AWS_SECRET_ACCESS_KEY=sua_secret_key_aqui")
            return
        
        # Inicializa o gerenciador EC2
        ec2_manager = EC2Manager()
        
        # Testa a conexão com EC2
        print("\n1. Testando conexão com EC2...")
        instances = ec2_manager.list_instances()
        print("✓ Conexão com EC2 estabelecida com sucesso!")
        
        # Obtém informações da instância específica
        print("\n2. Obtendo informações da instância...")
        instance = ec2_manager.get_instance(INSTANCE_ID)
        
        if instance:
            print("\nInformações da Instância:")
            print("-" * 30)
            print(f"ID: {instance.id}")
            print(f"Estado: {instance.state['Name']}")
            print(f"Tipo: {instance.instance_type}")
            print(f"DNS Público: {instance.public_dns_name}")
            print(f"IP Público: {instance.public_ip_address}")
            print(f"Tags: {instance.tags if instance.tags else 'Nenhuma'}")
            
            # Exibe comando SSH
            print("\nComando SSH para conexão:")
            print(f"ssh -i \"~/{KEY_PAIR_NAME}.pem\" ec2-user@{instance.public_dns_name}")
            
            # Obtém métricas da instância
            print("\n3. Obtendo métricas da instância...")
            metrics = ec2_manager.get_instance_metrics(INSTANCE_ID)
            
            if metrics['cpu']:
                print("\nMétricas de CPU:")
                print(f"Último valor: {metrics['cpu'][-1]['value']:.2f}%")
                print(f"Timestamp: {format_timestamp(metrics['cpu'][-1]['timestamp'])}")
            
            if metrics['memory']:
                print("\nMétricas de Memória:")
                print(f"Último valor: {metrics['memory'][-1]['value']:.2f}%")
                print(f"Timestamp: {format_timestamp(metrics['memory'][-1]['timestamp'])}")
            
            if metrics['disk']:
                print("\nMétricas de Disco:")
                print(f"Último valor: {metrics['disk'][-1]['value']:.2f}%")
                print(f"Timestamp: {format_timestamp(metrics['disk'][-1]['timestamp'])}")
            
            if metrics['network']:
                print("\nMétricas de Rede:")
                last_network = metrics['network'][-1]
                print(f"Entrada: {last_network['in'] / 1024 / 1024:.2f} MB")
                print(f"Saída: {last_network['out'] / 1024 / 1024:.2f} MB")
                print(f"Timestamp: {format_timestamp(last_network['timestamp'])}")
            
            print("\n✓ Todas as métricas foram obtidas com sucesso!")
            
        else:
            print(f"\n❌ Instância {INSTANCE_ID} não encontrada!")
            print("\nVerifique se:")
            print("1. O ID da instância está correto no arquivo .env")
            print("2. A instância está em execução")
            print("3. Você tem permissão para acessar esta instância")
        
        print("\n=== Teste de Conexão Concluído ===")
        print("=" * 50)
        
    except ClientError as e:
        print(f"\n❌ Erro de autenticação AWS: {e}")
        print("\nVerifique se suas credenciais AWS estão configuradas corretamente no arquivo .env")
    except Exception as e:
        print(f"\n❌ Erro durante o teste: {e}")
        print("\nVerifique se:")
        print("1. Suas credenciais AWS estão corretas")
        print("2. A instância está em execução")
        print("3. Você tem as permissões necessárias")
        print("4. A região está configurada corretamente")

if __name__ == "__main__":
    test_aws_connection() 