function formatCurrency(input) {
    let value = input.value.replace(/\D/g, '');
    value = (value / 100).toFixed(2) + '';
    value = value.replace('.', ',');
    value = value.replace(/(\d)(?=(\d{3})+\,)/g, '$1.');
    input.value = 'R$ ' + value;
}

function prepareForm() {
    const input = document.getElementById('requisitado');
    const hiddenInput = document.getElementById('requisitado_hidden');
    let value = input.value.replace(/[^\d,]/g, '').replace(',', '.');
    hiddenInput.value = parseFloat(value).toFixed(2);
}

