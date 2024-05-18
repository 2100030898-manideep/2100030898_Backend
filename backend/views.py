from django.shortcuts import render
from django.db import connection
from .models import Customer, Product, Order, OrderItem


def get_all(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Customers")
        customers = cursor.fetchall()

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Orders WHERE YEAR(OrderDate) = 2023 AND MONTH(OrderDate) = 1")
        january_orders = cursor.fetchall()

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT Orders.OrderID, Orders.OrderDate, Customers.FirstName, Customers.LastName, Customers.Email
            FROM Orders
            JOIN Customers ON Orders.CustomerID = Customers.CustomerID
        """)
        orders_with_customer_details = cursor.fetchall()

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT Products.ProductName, OrderItems.Quantity
            FROM OrderItems
            JOIN Products ON OrderItems.ProductID = Products.ProductID
            WHERE OrderItems.OrderID = 1
        """)
        products_in_order = cursor.fetchall()

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT Customers.CustomerID, Customers.FirstName, Customers.LastName, 
                   SUM(Products.Price * OrderItems.Quantity) AS TotalSpent
            FROM Customers
            JOIN Orders ON Customers.CustomerID = Orders.CustomerID
            JOIN OrderItems ON Orders.OrderID = OrderItems.OrderID
            JOIN Products ON OrderItems.ProductID = Products.ProductID
            GROUP BY Customers.CustomerID, Customers.FirstName, Customers.LastName
        """)
        total_spent_by_customer = cursor.fetchall()

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT Products.ProductID, Products.ProductName, 
                   SUM(OrderItems.Quantity) AS TotalOrdered
            FROM OrderItems
            JOIN Products ON OrderItems.ProductID = Products.ProductID
            GROUP BY Products.ProductID, Products.ProductName
            ORDER BY TotalOrdered DESC
            LIMIT 1
        """)
        most_popular_product = cursor.fetchall()

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT DATE_FORMAT(OrderDate, '%Y-%m') AS Month, 
                   COUNT(*) AS TotalOrders, 
                   SUM(Products.Price * OrderItems.Quantity) AS TotalSales
            FROM Orders
            JOIN OrderItems ON Orders.OrderID = OrderItems.OrderID
            JOIN Products ON OrderItems.ProductID = Products.ProductID
            WHERE YEAR(OrderDate) = 2023
            GROUP BY Month
        """)
        monthly_sales = cursor.fetchall()

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT Customers.CustomerID, Customers.FirstName, Customers.LastName, 
                   SUM(Products.Price * OrderItems.Quantity) AS TotalSpent
            FROM Customers
            JOIN Orders ON Customers.CustomerID = Orders.CustomerID
            JOIN OrderItems ON Orders.OrderID = OrderItems.OrderID
            JOIN Products ON OrderItems.ProductID = Products.ProductID
            GROUP BY Customers.CustomerID, Customers.FirstName, Customers.LastName
            HAVING TotalSpent > 1000
        """)
        big_spender_customers = cursor.fetchall()

    context = {
        'customers': customers,
        'january_orders': january_orders,
        'orders_with_customer_details': orders_with_customer_details,
        'products_in_order': products_in_order,
        'total_spent_by_customer': total_spent_by_customer,
        'most_popular_product': most_popular_product,
        'monthly_sales': monthly_sales,
        'big_spender_customers': big_spender_customers
    }

    def all_data(request):
        customers = Customer.objects.all()
        orders = Order.objects.filter(order_date__year=2023, order_date__month=1)
        order_items = OrderItem.objects.select_related('product').all()
        products = Product.objects.all()

        context = {
            'customers': customers,
            'orders': orders,
            'order_items': order_items,
            'products': products,
        }
        return render(request, 'all.html', context)
