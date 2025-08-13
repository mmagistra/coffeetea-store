function updateVariations(productSelect) {
    const currentUrl = window.location.href;
    const rootUrl = new URL(currentUrl).origin;

    const productId = productSelect.value;
    const row = productSelect.closest('tr') || productSelect.closest('.form-row');
    const variationSelect = row.querySelector(`#id_items-${row.id.split('-')[1]}-variation`);
    if (!variationSelect) {
        console.error('Variation select not found');
        return;
    }

    variationSelect.innerHTML = '<option value="">Загрузка...</option>';
    variationSelect.disabled = true;

    if (!productId) {
        variationSelect.innerHTML = '<option value="">Сначала выберите товар</option>';
        variationSelect.disabled = true;
        return;
    }

    fetch(rootUrl + `/api/v1/products/get-variations/${productId}/`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            variationSelect.innerHTML = '<option value="">Выберите вариацию</option>';

            if (data.variations && data.variations.length > 0) {
                data.variations.forEach(variation => {
                    const option = document.createElement('option');
                    option.value = variation.id;
                    option.textContent = `${variation.text_description_of_count} (${variation.price}₽)`;
                    variationSelect.appendChild(option);
                });
                variationSelect.disabled = false;
            } else {
                variationSelect.innerHTML = '<option value="">Нет доступных вариаций</option>';
                variationSelect.disabled = true;
            }
        })
        .catch(error => {
            console.error('Error loading variations:', error);
            variationSelect.innerHTML = '<option value="">Ошибка загрузки</option>';
            variationSelect.disabled = true;
        });
}

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.product-selector').forEach(select => {
        select.addEventListener('change', function() {
            updateVariations(this);
        });
    });

    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            mutation.addedNodes.forEach(function(node) {
                if (node.nodeType === 1 && node.tagName === 'TR') {
                    const productSelect = node.querySelector('.product-selector');
                    if (productSelect && !productSelect.hasAttribute('data-listener-added')) {
                        productSelect.addEventListener('change', function() {
                            updateVariations(this);
                        });
                        productSelect.setAttribute('data-listener-added', 'true');
                    }
                }
            });
        });
    });

    const inlineGroup = document.querySelector('.inline-group tbody');
    if (inlineGroup) {
        observer.observe(inlineGroup, { childList: true, subtree: true });
    }
});
