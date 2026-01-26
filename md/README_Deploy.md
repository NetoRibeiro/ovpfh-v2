# 🚀 Guia de Deploy - Hostinger (VPS)

Este guia explica como configurar o site **Onde Vai Passar Futebol Hoje** em uma **VPS Hostinger**, permitindo automação e melhor controle do ambiente.

## 📋 Pré-requisitos
- VPS Hostinger ativa (Ubuntu 22.04+ recomendado).
- Acesso SSH.
- Domínio apontando para o IP da VPS.

---

## 🛠️ Passo 1: Configuração do Servidor

Conecte-se à sua VPS via SSH e instale as dependências básicas:

```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx git -y
```

---

## 📂 Passo 2: Clonagem e Ambiente

1. Clone seu repositório:
   ```bash
   cd /var/www
   git clone https://github.com/SEU_USUARIO/ONDEVAIPASSARFUTEBOLHOJE.git
   cd ONDEVAIPASSARFUTEBOLHOJE
   ```

2. Configure o ambiente virtual:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt  # Se houver
   ```

---

## ⚙️ Passo 3: Configuração do NGINX

Configure o NGINX para servir o site e lidar com as URLs amigáveis:

1. Crie o arquivo de configuração:
   ```bash
   sudo nano /etc/nginx/sites-available/futebolhoje
   ```

2. Cole a configuração abaixo (ajuste o `server_name`):
   ```nginx
   server {
       listen 80;
       server_name ONDEVAIPASSARFUTEBOLHOJE.COM.BR www.ONDEVAIPASSARFUTEBOLHOJE.COM.BR;
       root /var/www/ONDEVAIPASSARFUTEBOLHOJE;
       index index.html;

       location / {
           try_files $uri $uri/ $uri.html =404;
       }

       # Garantir cache de ativos
       location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
           expires 30d;
           add_header Cache-Control "public, no-transform";
       }
   }
   ```

3. Ative o site e reinicie o NGINX:
   ```bash
   sudo ln -s /etc/nginx/sites-available/futebolhoje /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

---

## 🤖 Passo 4: Automação da Geração (Crontab)

Diferente da hospedagem compartilhada, na VPS você pode rodar o script SSG automaticamente.

1. Abra o editor de cron:
   ```bash
   crontab -e
   ```

2. Adicione uma linha para gerar as páginas a cada 1 hora (ou o intervalo que desejar):
   ```bash
   0 * * * * /var/www/ONDEVAIPASSARFUTEBOLHOJE/.venv/bin/python /var/www/ONDEVAIPASSARFUTEBOLHOJE/spiders/generate_match_pages.py >> /var/www/ONDEVAIPASSARFUTEBOLHOJE/generation.log 2>&1
   ```

---

## 🔄 Passo 5: Atualizando o Site

Para atualizar jogos sem precisar fazer upload manual:

1. Edite o `data/matches.json` no seu PC e faça `git push`.
2. Na VPS, rode:
   ```bash
   git pull
   # O script rodará sozinho no próximo ciclo do cron, 
   # ou você pode rodar manualmente agora:
   source .venv/bin/activate
   python spiders/generate_match_pages.py
   ```

---

## 🛡️ Passo 6: SSL (HTTPS) Gratis com Certbot

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d seu-dominio.com -d www.seu-dominio.com
```

---

© 2026 Onde Vai Passar Futebol Hoje

---

## ❓ FAQ - Dúvidas Comuns

**1. Onde fica o banco de dados?**
O site não usa banco de dados SQL. Ele usa arquivos JSON na pasta `data/`. É só editar o arquivo e subir.

**2. Posso rodar o script Python direto na Hostinger?**
Se você tiver um plano de **Hospedagem Compartilhada**, não. Você deve rodar no seu computador e subir os arquivos gerados. Se tiver uma **VPS**, você pode configurar um Cron Job para rodar o script.

**3. Site em branco ou 404?**
Verifique se você subiu a pasta `data/` e se o arquivo `.htaccess` está presente. Certifique-se de que os caminhos no `router.js` são relativos.

---

© 2026 Onde Vai Passar Futebol Hoje
