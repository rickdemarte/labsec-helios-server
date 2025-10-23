<?php
// ----------------------------------------------
// Arquivo: eleitore.php
// ----------------------------------------------
// Versão do PHP: 7.3
// ----------------------------------------------
// Dados de exemplo (CPF, Nome, Cidade, URL)
// Separados por vírgula, armazenados em string
$dados_csv = "
12345678901,João da Silva,Florianópolis,https://ufsc.br
11223344556,Maria do Norte,Chapecó,
";

// Converte a string CSV em matriz
$linhas = array_filter(array_map('trim', explode("\n", trim($dados_csv))));
$matriz = [];
foreach ($linhas as $linha) {
    $partes = array_map('trim', explode(',', $linha));
    $cpf    = $partes[0] ?? '';
    $nome   = $partes[1] ?? '';
    $cidade = $partes[2] ?? '';
    $url    = $partes[3] ?? '';

    $matriz[$cpf] = [
        'nome' => $nome,
        'cidade' => $cidade,
        'url' => $url
    ];
}

// Resultado padrão
$resultado = "";

// Se o formulário foi enviado
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $cpf_digitado = preg_replace('/\D/', '', $_POST['cpf'] ?? '');

    if (isset($matriz[$cpf_digitado])) {
        $dados = $matriz[$cpf_digitado];
        if (!empty($dados['url'])) {
            $resultado = "<div class='alert alert-success'>
                            <strong>{$dados['nome']}</strong><br>
                            Cidade: {$dados['cidade']}<br>
                            <a href='{$dados['url']}' target='_blank'>Acessar link</a>
                          </div>";
        } else {
            $resultado = "<div class='alert alert-warning'>
                            <strong>{$dados['nome']}</strong> - {$dados['cidade']}<br>
                            Esta área não possui candidatos na primeira fase da eleição.
                          </div>";
        }
    } else {
        $resultado = "<div class='alert alert-danger'>
                        Esse CPF não se inscreveu para essa eleição.
                      </div>";
    }
}
?>
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Consultar Eleitores</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css">
    <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery.mask/1.14.16/jquery.mask.min.js"></script>
    <script>
        $(document).ready(function(){
            $('#cpf').mask('000.000.000-00');
        });
    </script>
</head>
<body class="bg-light">
    <div class="container mt-5">
        <div class="card shadow p-4">
            <h3 class="text-center mb-3">Consulta de Eleitores</h3>
            <form method="POST" class="mb-3">
                <div class="mb-3">
                    <label for="cpf" class="form-label">Digite seu CPF:</label>
                    <input type="text" id="cpf" name="cpf" class="form-control" placeholder="000.000.000-00" required>
                </div>
                <button type="submit" class="btn btn-primary w-100">Consultar</button>
            </form>
            <?= $resultado ?>
        </div>
    </div>
</body>
</html>
