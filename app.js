document.addEventListener('DOMContentLoaded', function() {
    const db = firebase.firestore();
    const productsContainer = document.getElementById('products');
    const cartItemsContainer = document.getElementById('cart-items');
    let cart = [];

    // Firestore'dan ürünleri çek
    db.collection('products').get().then((querySnapshot) => {
        querySnapshot.forEach((doc) => {
            const product = doc.data();
            const productElement = document.createElement('div');
            productElement.innerHTML = `
                <h3>${product.name}</h3>
                <p>${product.description}</p>
                <p>Price: $${product.price}</p>
                <button data-id="${doc.id}">Add to Cart</button>
            `;
            productsContainer.appendChild(productElement);
        });

        // Sepete ekleme işlemi
        productsContainer.addEventListener('click', (e) => {
            if (e.target.tagName === 'BUTTON') {
                const productId = e.target.getAttribute('data-id');
                const productDoc = querySnapshot.docs.find(doc => doc.id === productId);
                const product = productDoc.data();
                cart.push(product);
                updateCart();
            }
        });
    });

    function updateCart() {
        cartItemsContainer.innerHTML = '';
        cart.forEach((item, index) => {
            const cartItem = document.createElement('li');
            cartItem.textContent = `${item.name} - $${item.price}`;
            cartItemsContainer.appendChild(cartItem);
        });
    }
});
