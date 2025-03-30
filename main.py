from ec2_manager import EC2Manager
import os

def main():
    # Inicializa o gerenciador EC2
    ec2_manager = EC2Manager()
    
    try:
        # Lista todas as instâncias existentes
        print("Listando instâncias existentes...")
        instances = ec2_manager.list_instances()
        
        # Encontra a instância específica
        target_instance = None
        for instance in instances:
            if instance.id == 'i-05249f744fa92653c':  # ID da sua instância existente
                target_instance = instance
                break
        
        if target_instance:
            print("\nDetalhes da instância:")
            print(f"ID: {target_instance.id}")
            print(f"Estado: {target_instance.state['Name']}")
            print(f"Tipo: {target_instance.instance_type}")
            print(f"DNS Público: {target_instance.public_dns_name}")
            print(f"Tags: {target_instance.tags}")
            
            # Usa o caminho absoluto do arquivo .pem
            pem_path = os.path.expanduser("~/MyInstance.pem")
            print("\nPara conectar à instância, use o comando:")
            print(f"ssh -i \"{pem_path}\" ec2-user@{target_instance.public_dns_name}")
            
            # Monitora recursos da instância
            ec2_manager.monitor_instance_resources(target_instance.id)
        else:
            print("Instância não encontrada!")
        
    except Exception as e:
        print(f"Erro durante a execução: {e}")

if __name__ == "__main__":
    main() 