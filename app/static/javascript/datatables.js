$(document).ready(function() {
    // Configuração da tabela RREO
    var tableRREO = $('#tabelaOperacoes').DataTable({
        "ajax": {
            "url": "/dados_rreo",
            "data": function(d) {
                d.ano = $('#anoSelectRREO').val();
            }
        },
        "columns": [
            { "data": "id" },
            { "data": "exercicio" },
            { "data": "periodo" },
            { "data": "anexo" },
            { "data": "coluna" },
            { "data": "conta" },
            { "data": "valor" }
        ],
        "columnDefs": [
            { "width": "5%", "targets": 0 },  // ID menor
            { "width": "10%", "targets": 1 }, // Ano
            { "width": "5%", "targets": 2 }, // Bimestre
            { "width": "15%", "targets": 3 }, // anexo
            { "width": "25%", "targets": 4 }, // Movimentação Contábil maior
            { "width": "25%", "targets": 5 }, // Natureza maior
            { "width": "15%", "targets": 6 },  // Valor
        ],
        "autoWidth": false, // Desativa ajuste automático de largura
        "language": {
            "url": "/static/javascript/pt_br.json"
        },
        "paging": true,
        "ordering": true,
        "info": true,
        "responsive": true,
        "dom": 'Bfrtip',
        "buttons": [
            'copy', 'csv', 'excel', 'pdf'
        ]
    });

    // Captura o evento de mudança do select RREO
    $('#anoSelectRREO').change(function() {
        tableRREO.ajax.reload();
    });

    // Captura o evento de submit do formulário RREO
    $('#formFiltroRREO').submit(function(event) {
        event.preventDefault(); // Impede o comportamento padrão de submit

        // Obtém o ano selecionado
        var anoSelecionado = $('#anoSelectRREO').val();

        // Atualiza os dados da tabela com o novo ano
        tableRREO.ajax.url("/dados_rreo?ano=" + anoSelecionado).load();
    });

    // Configuração da tabela RGF
    var tableRGF = $('#tabelaRGF').DataTable({
        "ajax": {
            "url": "/dados_rgf",
            "data": function(d) {
                d.ano = $('#anoSelectRGF').val();
            }
        },
        "columns": [
            { "data": "id" },
            { "data": "exercicio" },
            { "data": "periodo" },
            { "data": "anexo" },
            { "data": "coluna" },
            { "data": "conta" },
            { "data": "valor" }
        ],
        "columnDefs": [
            { "width": "5%", "targets": 0 },  // ID menor
            { "width": "10%", "targets": 1 }, // Ano
            { "width": "5%", "targets": 2 }, // Bimestre
            { "width": "15%", "targets": 3 }, // anexo
            { "width": "25%", "targets": 4 }, // Movimentação Contábil maior
            { "width": "25%", "targets": 5 }, // Natureza maior
            { "width": "15%", "targets": 6 },  // Valor
        ],
        "autoWidth": false, // Desativa ajuste automático de largura
        "language": {
            "url": "/static/javascript/pt_br.json"
        },
        "paging": true,
        "ordering": true,
        "info": true,
        "responsive": true,
        "dom": 'Bfrtip',
        "buttons": [
            'copy', 'csv', 'excel', 'pdf'
        ]
    });

    // Captura o evento de mudança do select RGF
    $('#anoSelectRGF').change(function() {
        tableRGF.ajax.reload();
    });

    // Captura o evento de submit do formulário RGF
    $('#formFiltroRGF').submit(function(event) {
        event.preventDefault(); // Impede o comportamento padrão de submit

        // Obtém o ano selecionado
        var anoSelecionado = $('#anoSelectRGF').val();

        // Atualiza os dados da tabela com o novo ano
        tableRGF.ajax.url("/dados_rgf?ano=" + anoSelecionado).load();
    });
});

