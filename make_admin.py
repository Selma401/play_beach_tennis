from werkzeug.security import generate_password_hash
email = "admin@portbeachtennis.com"
nome = "Admin"
senha = "admin123"
h = generate_password_hash(senha)
print("Hash gerado:", h)
print("SQL para inserir (copie e execute no MySQL):")
print("INSERT INTO usuarios (nome, email, senha, is_admin) VALUES ('{}', '{}', '{}', 1);".format(nome, email, h))
