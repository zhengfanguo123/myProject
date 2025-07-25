$(function(){
    const categories = [
        { id: 'coffee', name: 'Coffee' },
        { id: 'tea', name: 'Tea' },
        { id: 'pastries', name: 'Pastries' },
        { id: 'bread', name: 'Bread' },
        { id: 'sandwiches', name: 'Sandwiches' }
    ];

    const items = {
        coffee: [
            { id: 1, name: 'Latte', price: 3.5 },
            { id: 2, name: 'Espresso', price: 2.5 }
        ],
        tea: [
            { id: 3, name: 'Green Tea', price: 2.0 }
        ],
        pastries: [
            { id: 4, name: 'Croissant', price: 2.5 }
        ],
        bread: [],
        sandwiches: []
    };

    const cart = [];

    function renderCategories(){
        const catEl = $('.categories').empty();
        categories.forEach(c => {
            const btn = $('<button>').text(c.name).data('id', c.id).addClass('cat-btn');
            catEl.append(btn);
        });
    }

    function renderItems(cat){
        const itemEl = $('.items').empty();
        (items[cat] || []).forEach(i => {
            const card = $('<div>').addClass('item-card');
            card.append($('<div>').addClass('item-name').text(i.name));
            card.append($('<div>').addClass('item-price').text('$'+i.price.toFixed(2)));
            const add = $('<button>').text('Add').data('item', i);
            card.append(add);
            itemEl.append(card);
        });
    }

    function updateCart(){
        const list = $('.cart-items').empty();
        let total = 0;
        cart.forEach(i => {
            const li = $('<li>').text(i.name + ' $' + i.price.toFixed(2));
            list.append(li);
            total += i.price;
        });
        $('.total').text('Total: $' + total.toFixed(2));
    }

    $('.categories').on('click', '.cat-btn', function(){
        const id = $(this).data('id');
        renderItems(id);
    });

    $('.items').on('click', 'button', function(){
        const item = $(this).data('item');
        cart.push(item);
        updateCart();
    });

    $('#checkout-btn').click(function(){
        alert('Checkout not implemented');
    });

    renderCategories();
    renderItems('coffee');
});
