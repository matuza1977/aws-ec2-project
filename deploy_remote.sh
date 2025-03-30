#!/bin/bash

# Configuração da conexão SSH
SSH_KEY="/Users/chris/MyInstance.pem"
INSTANCE_HOST="ec2-user@ec2-56-125-31-181.sa-east-1.compute.amazonaws.com"
SSH_CMD="ssh -i \"$SSH_KEY\" $INSTANCE_HOST"
SCP_CMD="scp -i \"$SSH_KEY\""

# Verifica se o arquivo de chave existe
if [ ! -f "$SSH_KEY" ]; then
    echo "Erro: Arquivo de chave não encontrado em $SSH_KEY"
    exit 1
fi

# Configura as permissões corretas para a chave
chmod 600 "$SSH_KEY"

# Cria um diretório temporário para os arquivos de deploy
TEMP_DIR="deploy_temp"
mkdir -p $TEMP_DIR

# Copia os arquivos necessários para o diretório temporário
cp app.py $TEMP_DIR/
cp ec2_manager.py $TEMP_DIR/
cp config.py $TEMP_DIR/
cp requirements.txt $TEMP_DIR/
cp -r static $TEMP_DIR/
cp -r templates $TEMP_DIR/
cp .env $TEMP_DIR/
cp nginx.conf $TEMP_DIR/
cp aws-ec2-dashboard.service $TEMP_DIR/

# Cria o script de instalação na instância
cat > $TEMP_DIR/install.sh << 'EOL'
#!/bin/bash

# Atualiza o sistema
sudo yum update -y

# Instala as dependências do sistema
sudo yum install -y python3 python3-pip nginx

# Cria o diretório do projeto
mkdir -p /home/ec2-user/aws-ec2-projeto
cd /home/ec2-user/aws-ec2-projeto

# Cria e ativa o ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instala as dependências do Python
pip install -r requirements.txt
pip install gunicorn

# Configura o Nginx
sudo cp nginx.conf /etc/nginx/conf.d/aws-ec2-dashboard.conf
sudo rm /etc/nginx/conf.d/default.conf
sudo nginx -t
sudo systemctl restart nginx

# Configura o serviço systemd
sudo cp aws-ec2-dashboard.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable aws-ec2-dashboard
sudo systemctl start aws-ec2-dashboard

# Configura as permissões
sudo chown -R ec2-user:ec2-user /home/ec2-user/aws-ec2-projeto

echo "Deploy concluído! O dashboard está disponível em http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
EOL

# Testa a conexão SSH antes de prosseguir
echo "Testando conexão SSH com a instância..."
if ! eval "$SSH_CMD" "echo 'Conexão SSH estabelecida com sucesso!'"; then
    echo "Erro: Não foi possível conectar à instância EC2"
    echo "Verifique se:"
    echo "1. A instância está rodando"
    echo "2. O arquivo de chave tem as permissões corretas"
    exit 1
fi

# Copia os arquivos para a instância
echo "Copiando arquivos para a instância..."
eval "$SCP_CMD" -r $TEMP_DIR/* "$INSTANCE_HOST:/home/ec2-user/aws-ec2-projeto/"

# Executa o script de instalação na instância
echo "Executando script de instalação na instância..."
eval "$SSH_CMD" "cd /home/ec2-user/aws-ec2-projeto && chmod +x install.sh && ./install.sh"

# Remove o diretório temporário
rm -rf $TEMP_DIR

echo "Deploy concluído! O dashboard está disponível em http://ec2-56-125-31-181.sa-east-1.compute.amazonaws.com" 