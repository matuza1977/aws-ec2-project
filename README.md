# Dashboard de Monitoramento AWS EC2

Este projeto é um dashboard web para monitoramento de instâncias EC2 na AWS, desenvolvido em Python com Flask e utilizando a AWS SDK (boto3).

## Estrutura do Projeto

```
aws-ec2-projeto/
├── static/
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   └── script.js
│   └── img/
├── templates/
│   └── index.html
├── app.py
├── ec2_manager.py
├── config.py
├── requirements.txt
└── .env
```

## Pré-requisitos

### Sistema Operacional
- macOS (testado na versão 14.0 ou superior)

### Ferramentas de Desenvolvimento
1. Python 3.8 ou superior
2. pip (gerenciador de pacotes Python)
3. Git (para controle de versão)

### Pacotes do Sistema (macOS)
```bash
# Instalar Homebrew (se ainda não tiver)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Instalar Python e Git
brew install python git
```

### Configuração AWS
1. Conta AWS com acesso programático
2. Credenciais AWS configuradas
3. Instância EC2 em execução na região sa-east-1
4. Chave de acesso SSH (MyInstance.pem)

## Instalação

1. Clone o repositório:
```bash
git clone <url-do-repositorio>
cd aws-ec2-projeto
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

## Configuração AWS

1. Instale o AWS CLI:
```bash
brew install awscli
```

2. Configure suas credenciais AWS:
```bash
aws configure
```
- AWS Access Key ID: [sua-access-key]
- AWS Secret Access Key: [sua-secret-key]
- Default region name: sa-east-1
- Default output format: json

3. Configure as permissões da chave SSH:
```bash
chmod 400 ~/MyInstance.pem
```

## Dependências do Projeto

### Pacotes Python
- boto3==1.34.69 (AWS SDK para Python)
- python-dotenv==1.0.1 (Gerenciamento de variáveis de ambiente)
- pandas==2.2.1 (Manipulação de dados)
- flask==3.0.2 (Framework web)
- psutil==5.9.8 (Monitoramento de recursos do sistema)

### Bibliotecas JavaScript
- Chart.js (Visualização de gráficos)
- Font Awesome 6.0.0 (Ícones)

## Executando o Projeto

1. Ative o ambiente virtual (se ainda não estiver ativo):
```bash
source venv/bin/activate
```

2. Inicie o servidor Flask:
```bash
python app.py
```

3. Acesse o dashboard:
```
http://localhost:5000
```

## Funcionalidades

- Monitoramento em tempo real de recursos EC2
- Visualização de métricas (CPU, Memória, Disco, Rede)
- Gráficos interativos
- Informações de conexão SSH
- Atualização automática a cada 5 minutos
- Interface responsiva

## Segurança

- Credenciais AWS armazenadas em variáveis de ambiente
- Chave SSH com permissões restritas (400)
- Comunicação segura via HTTPS (quando configurado)

## Solução de Problemas

1. Erro de permissão na chave SSH:
```bash
chmod 400 ~/MyInstance.pem
```

2. Erro de autenticação AWS:
- Verifique suas credenciais em `~/.aws/credentials`
- Confirme se as credenciais têm as permissões necessárias

3. Erro de conexão com a instância:
- Verifique se a instância está em execução
- Confirme se o grupo de segurança permite acesso SSH
- Verifique se está usando a chave SSH correta

## Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

   ![image](https://github.com/user-attachments/assets/7230b1a3-e4aa-4065-a5a5-478a3d84b115)

   ![image](https://github.com/user-attachments/assets/94061cb5-0a37-47ea-818a-c87629d285c5)

   ![image](https://github.com/user-attachments/assets/19210fc4-51fc-483a-aa39-ca305515a8de)




## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes. 
