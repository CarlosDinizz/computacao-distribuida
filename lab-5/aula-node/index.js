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

const ERRO_ID_INVALIDO = {
    error: "INVALID_ID",
    message: "O ID deve ser um inteiro positivo"
};

function idValido(valor) {
    return /^[0-9]+$/.test(String(valor)) && Number(valor) > 0;
}

function erroNaoEncontrado(res, id) {
    return res.status(404).json({
        error: "NOT_FOUND",
        message: `Produto com ID ${id} não encontrado`
    });
}

app.param('id', (req, res, next, id) => {
    if (!idValido(id)) {
        return res.status(400).json(ERRO_ID_INVALIDO);
    }
    req.params.id = String(Number(id));
    next();
});

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
    if (!dado_encontrado) return erroNaoEncontrado(res, id);
    res.json(dado_encontrado);
})

app.get('/estoque/:id', (req, res) => {
    const id = req.params.id;
    const produto = produtos_estoque[id];
    if (!produto) return erroNaoEncontrado(res, id);
    res.json({ id, ...produto });
})

app.get('/api/full-info/:id', async (req, res) => {
    const id = req.params.id;
    try {
        const response = await fetch(`${FLASK_URL}/detalhes/${id}`, { method: 'get' });
        const flaskResponse = await response.json();

        if (!response.ok) {
            return res.status(response.status).json(flaskResponse);
        }
        if (!produtos_estoque[id]) return erroNaoEncontrado(res, id);

        const nodeResponse = {
            nome: produtos_estoque[id].nome,
            preco: flaskResponse["preco"],
        }
        res.json(nodeResponse);
    } catch (error) {
        return res.status(502).json({
            error: "FLASK_UNAVAILABLE",
            message: "Não foi possível consultar o servidor Flask"
        });
    }
})

app.post('/api/cadastrar', async (req, res) => {
    try {
        const { id, nome, estoque, preco_base, categoria } = req.body ?? {};

        if (!idValido(id)) {
            return res.status(400).json(ERRO_ID_INVALIDO);
        }

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

app.get('/status', (req, res) => {
    try {
        
        const response = {
            service: 'node',
            status: 'online',
            timestamp: new Date().toISOString()
        };
        return res.status(200).json(response);
    } catch (error) {
        return res.status(500).json({message: 'Erro no servidor'})
    }
})

app.listen(PORT, () => {
    console.log(`Servidor Node rodando na porta ${PORT}`);
});
