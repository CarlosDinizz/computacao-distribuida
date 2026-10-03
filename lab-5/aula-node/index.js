
const express = require('express');

const app = express();

const PORT = 3000;

app.use(express.json());

const produtos_estoque = { 
        1: 
            { 
                nome: "Dell XPS 13", 
                estoque: 1,
            }, 
        2: { 
            nome: "Monitor LG 29", 
            estoque: 5,
        }
    }

app.get('/api/data', (req, res) => {
    res.json({
        "mensagem": "Olá do Node.js!",
        "status": "sucesso",
        "tecnologia": "JavaScript"
    });
});

app.get('/api/data/:id', (req, res) => {
    const id = req.params.id
    const dado_encontrado = produtos_estoque[id];
    console.log(dado_encontrado)
    res.json(dado_encontrado);
})

app.listen(PORT, () => {
    console.log(`Servidor Node rodando na porta ${PORT}`);
});