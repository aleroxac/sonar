const express = require('express');

const app = express();
app.disable("x-powered-by");

const healthcheck = (req, res) => {
    res.json({ status: 'UP' });
};

app.get('/status', healthcheck);

if (require.main === module) {
    const port = 8080;
    app.listen(port, '0.0.0.0', () => {
        console.log(`Server is running on port ${port}`);
    });
}

module.exports = { app, healthcheck };
