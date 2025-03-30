import boto3
from botocore.exceptions import ClientError
from config import AWS_REGION
from datetime import datetime, timedelta
import pandas as pd

class EC2Manager:
    def __init__(self):
        self.ec2_client = boto3.client('ec2', region_name=AWS_REGION)
        self.ec2_resource = boto3.resource('ec2', region_name=AWS_REGION)
        self.cloudwatch = boto3.client('cloudwatch', region_name=AWS_REGION)

    def get_instance(self, instance_id):
        """Retorna a instância EC2 pelo ID."""
        try:
            instance = self.ec2_resource.Instance(instance_id)
            # Verifica se a instância existe
            instance.load()
            return instance
        except ClientError as e:
            print(f"Erro ao obter instância: {e}")
            return None

    def list_instances(self):
        """Lista todas as instâncias EC2."""
        try:
            instances = self.ec2_resource.instances.all()
            for instance in instances:
                print(f"ID: {instance.id}")
                print(f"Estado: {instance.state['Name']}")
                print(f"Tipo: {instance.instance_type}")
                print(f"DNS Público: {instance.public_dns_name}")
                print(f"Tags: {instance.tags}")
                print("-" * 50)
            return instances
        except ClientError as e:
            print(f"Erro ao listar instâncias: {e}")
            raise

    def get_instance_status(self, instance_id):
        """Retorna o status atual da instância."""
        try:
            instance = self.ec2_resource.Instance(instance_id)
            return instance.state['Name']
        except ClientError as e:
            print(f"Erro ao obter status da instância: {e}")
            raise

    def get_instance_public_dns(self, instance_id):
        """Retorna o endereço DNS público da instância."""
        try:
            instance = self.ec2_resource.Instance(instance_id)
            return instance.public_dns_name
        except ClientError as e:
            print(f"Erro ao obter DNS público: {e}")
            raise

    def get_instance_metrics(self, instance_id, hours=1):
        """Obtém todas as métricas da instância do CloudWatch."""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=hours)
            
            # CPU
            cpu_values = self.cloudwatch.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='CPUUtilization',
                Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                StartTime=start_time,
                EndTime=end_time,
                Period=300,
                Statistics=['Average']
            )
            
            # Memória
            memory_values = self.cloudwatch.get_metric_statistics(
                Namespace='System/Linux',
                MetricName='MemoryUtilization',
                Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                StartTime=start_time,
                EndTime=end_time,
                Period=300,
                Statistics=['Average']
            )
            
            # Disco
            disk_values = self.cloudwatch.get_metric_statistics(
                Namespace='System/Linux',
                MetricName='DiskSpaceUtilization',
                Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                StartTime=start_time,
                EndTime=end_time,
                Period=300,
                Statistics=['Average']
            )
            
            # Rede
            network_in = self.cloudwatch.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='NetworkIn',
                Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                StartTime=start_time,
                EndTime=end_time,
                Period=300,
                Statistics=['Average']
            )
            
            network_out = self.cloudwatch.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='NetworkOut',
                Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                StartTime=start_time,
                EndTime=end_time,
                Period=300,
                Statistics=['Average']
            )
            
            # Formata os dados para retorno
            return {
                'cpu': [{'timestamp': v['Timestamp'].isoformat(), 'value': v['Average']} for v in cpu_values.get('Datapoints', [])],
                'memory': [{'timestamp': v['Timestamp'].isoformat(), 'value': v['Average']} for v in memory_values.get('Datapoints', [])],
                'disk': [{'timestamp': v['Timestamp'].isoformat(), 'value': v['Average']} for v in disk_values.get('Datapoints', [])],
                'network': [
                    {
                        'timestamp': v['Timestamp'].isoformat(),
                        'in': v['Average'],
                        'out': next((o['Average'] for o in network_out.get('Datapoints', []) if o['Timestamp'] == v['Timestamp']), 0)
                    }
                    for v in network_in.get('Datapoints', [])
                ]
            }
            
        except ClientError as e:
            print(f"Erro ao obter métricas: {e}")
            return {
                'cpu': [],
                'memory': [],
                'disk': [],
                'network': []
            }

    def monitor_instance_resources(self, instance_id):
        """Monitora recursos da instância (CPU, memória, disco, rede)."""
        try:
            print(f"\nMonitorando recursos da instância {instance_id}")
            print("=" * 50)
            
            # CPU
            cpu_values = self.get_instance_metrics(instance_id, 'CPUUtilization')
            if cpu_values:
                print("\nUtilização de CPU:")
                print(f"Último valor: {cpu_values[-1]['Average']:.2f}%")
                print(f"Média: {sum(v['Average'] for v in cpu_values) / len(cpu_values):.2f}%")
            
            # Memória (requer CloudWatch Agent instalado na instância)
            memory_values = self.get_instance_metrics(instance_id, 'MemoryUtilization')
            if memory_values:
                print("\nUtilização de Memória:")
                print(f"Último valor: {memory_values[-1]['Average']:.2f}%")
                print(f"Média: {sum(v['Average'] for v in memory_values) / len(memory_values):.2f}%")
            
            # Disco (requer CloudWatch Agent instalado na instância)
            disk_values = self.get_instance_metrics(instance_id, 'DiskSpaceUtilization')
            if disk_values:
                print("\nUtilização de Disco:")
                print(f"Último valor: {disk_values[-1]['Average']:.2f}%")
                print(f"Média: {sum(v['Average'] for v in disk_values) / len(disk_values):.2f}%")
            
            # Rede
            network_in = self.get_instance_metrics(instance_id, 'NetworkIn')
            network_out = self.get_instance_metrics(instance_id, 'NetworkOut')
            
            if network_in and network_out:
                print("\nTráfego de Rede:")
                print(f"Entrada: {network_in[-1]['Average'] / 1024 / 1024:.2f} MB")
                print(f"Saída: {network_out[-1]['Average'] / 1024 / 1024:.2f} MB")
            
            print("\nNota: Algumas métricas podem não estar disponíveis se o CloudWatch Agent não estiver instalado na instância.")
            
        except Exception as e:
            print(f"Erro ao monitorar recursos: {e}") 