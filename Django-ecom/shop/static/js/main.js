document.addEventListener("DOMContentLoaded", function() {
    const cartList = document.querySelector(".cart-list");

    if (cartList) {
        cartList.addEventListener("click", function(event) {
            if (event.target.classList.contains("remove-from-cart")) {
                const cartItemId = event.target.dataset.cartItemId;

                // Send an AJAX request to remove the item
                fetch(`/remove_from_cart/${cartItemId}/`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            // If removal was successful, update the cart display
                            // For example, you can remove the cart item from the DOM
                            const cartItem = event.target.closest(".cart-item");
                            if (cartItem) {
                                cartItem.remove();
                            }

                            // Update the cart count in the offcanvas
                            const cartCount = document.querySelector("#cart-count-offcanvas");
                            if (cartCount) {
                                cartCount.textContent = data.cart_items_count;
                            }
                        } else {
                            // Handle error or display a message if removal failed
                            console.error("Item removal failed.");
                        }
                    });
            }
        });
    }
});




    document.addEventListener("DOMContentLoaded", function () {
        const addToCartButtons = document.querySelectorAll(".add-to-cart");
        const notification = document.getElementById("notification");
        const cartCountElement = document.querySelector("#cart-count");
    
        addToCartButtons.forEach((button) => {
            button.addEventListener("click", function () {
                const productId = this.getAttribute("data-product-id");
    
                // Send an AJAX POST request to add the product to the cart
                fetch("/add_to_cart/" + productId + "/", {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": getCookie("csrftoken"), // Include CSRF token
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({ product_id: productId }),
                })
                    .then((response) => response.json())
                    .then((data) => {
                        // Handle the response
                        if (data.success) {
                            notification.textContent = "Product added to cart!";
                            notification.classList.add("alert-success");
                            notification.classList.remove("d-none"); // Show the notification
    
                            // Update the cart count
                            cartCountElement.textContent = data.cart_items_count; // Update the cart count
    
                            setTimeout(() => {
                                notification.classList.add("d-none"); // Hide the notification after a delay
                                notification.classList.remove("alert-success");
                            }, 3000); // Hide after 3 seconds
                        } else {
                            notification.textContent = "Failed to add product to cart.";
                            notification.classList.add("alert-danger");
                            notification.classList.remove("d-none"); // Show the error notification
                            console.error("Failed to add product to cart.");
                        }
                    })
                    .catch((error) => {
                        console.error("Error:", error);
                    });
            });
        });
    });
    
    // Function to get CSRF token from cookies
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.startsWith(name + "=")) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
  
    // After successfully adding an item to the cart, update the cart count using AJAX
    fetch("/get_cart_count/", {
        method: "GET",
    })
        .then((response) => response.json())
        .then((data) => {
            // Update the cart count element with the new count
            const cartCountElement = document.querySelector("#cart-count");
            cartCountElement.textContent = data.cart_items_count;
        })
        .catch((error) => {
            console.error("Error updating cart count:", error);
        });

