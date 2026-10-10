
const express = require('express');
const app = express();
const PORT = 3000;
const FLASK_URL = "http://localhost:5000"

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

app.get('/api/data/produtos_estoque/:id', (req, res) => {
    const id = req.params.id
    const dado_encontrado = produtos_estoque[id];
    console.log(dado_encontrado)
    res.json(dado_encontrado);
})

app.get('/api/full-info/:id', async (req, res) => {
    const id = req.params.id;
    const response = await fetch(`${FLASK_URL}/detalhes/${id}`, { method: 'get' });
    const flaskResponse = await response.json();
    const nodeResponse = {
        nome: produtos_estoque[id].nome,
        preco: flaskResponse["preco"],
    }
    res.json(nodeResponse);
})

app.post('/api/cadastrar', async (req, res) => {
    try {
        const { id, nome, estoque, preco_base, categoria } = req.body;
        
        const payload = {
            id: id,
            preco_base,
            categoria: categoria
        }

        const response = await fetch(`${FLASK_URL}/fiscal/cadastrar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json' 
            },
            body: JSON.stringify(payload)
        });

        if (response.status === 201) {
            const dados = await response.json();
            
            produtos_estoque[id] = {
                nome: `${String(nome).toUpperCase()}`,
                estoque: estoque
            };
            
            return res.status(201).json({message: "Cadastro com sucesso!"});
        }

        return res.status(400).json({message: 'Não foi possível cadastrar o produto'});

    } catch (error) {
        return res.status(500).json({erro: "Erro no flask"})
    }
})


app.listen(PORT, () => {
    console.log(`Servidor Node rodando na porta ${PORT}`);
});