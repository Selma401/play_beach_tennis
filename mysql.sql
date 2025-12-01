CREATE DATABASE IF NOT EXISTS beach_tennis;
USE beach_tennis;

CREATE TABLE IF NOT EXISTS jogadores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    ranking INT,
    vitorias INT DEFAULT 0,
    derrotas INT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS partidas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_jogador_1 INT,
    id_jogador_2 INT,
    placar VARCHAR(50),
    data_partida DATE,
    FOREIGN KEY (id_jogador_1) REFERENCES jogadores(id),
    FOREIGN KEY (id_jogador_2) REFERENCES jogadores(id)
);

CREATE TABLE IF NOT EXISTS reserva (
  id INT AUTO_INCREMENT PRIMARY KEY,
  torneio_id INT NOT NULL,
  quadra VARCHAR(50) DEFAULT 'Quadra 1',
  horario TIME NOT NULL,
  reservado TINYINT(1) DEFAULT 0,
  usuario_id INT NULL,
  INDEX (torneio_id),
  INDEX (usuario_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;