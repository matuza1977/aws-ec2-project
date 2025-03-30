from flask import Flask, jsonify, send_from_directory, request
from ec2_manager import EC2Manager
import os
from dotenv import load_dotenv
from config import AWS_REGION, INSTANCE_ID, KEY_PAIR_NAME
from datetime import datetime

# Carrega as variáveis de ambiente
load_dotenv()

app = Flask(__name__, 
    static_folder='static',
    template_folder='templates'
)

def format_timestamp(timestamp):
    """Formata o timestamp para exibição."""
    return datetime.fromisoformat(timestamp).strftime('%d/%m/%Y %H:%M:%S')

def check_aws_credentials():
    """Verifica se as credenciais AWS estão configuradas."""
    if not os.getenv('AWS_ACCESS_KEY_ID') or not os.getenv('AWS_SECRET_ACCESS_KEY'):
        return False
    return True

@app.route('/')
def index():
    """Rota principal que serve o dashboard."""
    if not check_aws_credentials():
        return jsonify({
            'error': 'Credenciais AWS não configuradas',
            'message': 'Por favor, configure AWS_ACCESS_KEY_ID e AWS_SECRET_ACCESS_KEY no arquivo .env'
        }), 500
    return send_from_directory('templates', 'index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    """Serve arquivos estáticos (CSS, JS, imagens)."""
    return send_from_directory('static', path)

@app.route('/api/instance/<instance_id>')
def get_instance_info(instance_id):
    """API para obter informações da instância EC2."""
    try:
        if not check_aws_credentials():
            return jsonify({
                'error': 'Credenciais AWS não configuradas',
                'message': 'Por favor, configure AWS_ACCESS_KEY_ID e AWS_SECRET_ACCESS_KEY no arquivo .env'
            }), 500

        ec2_manager = EC2Manager()
        instance = ec2_manager.get_instance(instance_id)
        
        if instance:
            return jsonify({
                'id': instance.id,
                'state': instance.state['Name'],
                'type': instance.instance_type,
                'public_dns': instance.public_dns_name,
                'public_ip': instance.public_ip_address,
                'tags': instance.tags if instance.tags else [],
                'ssh_command': f"ssh -i \"~/{KEY_PAIR_NAME}.pem\" ec2-user@{instance.public_dns_name}"
            })
        return jsonify({
            'error': 'Instância não encontrada',
            'message': f'A instância {instance_id} não foi encontrada ou você não tem permissão para acessá-la.'
        }), 404
    except Exception as e:
        return jsonify({
            'error': 'Erro ao obter informações da instância',
            'message': str(e)
        }), 500

@app.route('/api/metrics/<instance_id>')
def get_instance_metrics(instance_id):
    """API para obter métricas da instância EC2."""
    try:
        if not check_aws_credentials():
            return jsonify({
                'error': 'Credenciais AWS não configuradas',
                'message': 'Por favor, configure AWS_ACCESS_KEY_ID e AWS_SECRET_ACCESS_KEY no arquivo .env'
            }), 500

        hours = int(request.args.get('hours', 1))
        ec2_manager = EC2Manager()
        metrics = ec2_manager.get_instance_metrics(instance_id, hours)
        
        # Formata os timestamps para exibição
        for metric_type in ['cpu', 'memory', 'disk']:
            if metrics[metric_type]:
                for point in metrics[metric_type]:
                    point['formatted_timestamp'] = format_timestamp(point['timestamp'])
        
        if metrics['network']:
            for point in metrics['network']:
                point['formatted_timestamp'] = format_timestamp(point['timestamp'])
                point['in_mb'] = point['in'] / 1024 / 1024
                point['out_mb'] = point['out'] / 1024 / 1024
        
        return jsonify(metrics)
    except Exception as e:
        return jsonify({
            'error': 'Erro ao obter métricas',
            'message': str(e)
        }), 500

@app.errorhandler(404)
def not_found_error(error):
    """Tratamento de erro 404 (página não encontrada)."""
    return jsonify({
        'error': 'Página não encontrada',
        'message': 'A página que você está procurando não existe.'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Tratamento de erro 500 (erro interno do servidor)."""
    return jsonify({
        'error': 'Erro interno do servidor',
        'message': 'Ocorreu um erro interno. Por favor, tente novamente mais tarde.'
    }), 500

if __name__ == '__main__':
    # Verifica as credenciais antes de iniciar o servidor
    if not check_aws_credentials():
        print("\n❌ Erro: Credenciais AWS não configuradas!")
        print("Por favor, configure as seguintes variáveis no arquivo .env:")
        print("AWS_ACCESS_KEY_ID=sua_access_key_aqui")
        print("AWS_SECRET_ACCESS_KEY=sua_secret_key_aqui")
    else:
        print("\n✓ Credenciais AWS configuradas com sucesso!")
        print(f"Região: {AWS_REGION}")
        print(f"ID da Instância: {INSTANCE_ID}")
        print(f"Par de Chaves: {KEY_PAIR_NAME}")
        print("\nIniciando servidor Flask...")
        app.run(debug=True) 