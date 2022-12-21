'''
This is where the back ends of the pages are handled
Each valid url is associated with a one of the functions
below which also display the appropriate .html file 
'''
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.db import connections, reset_queries
from django.shortcuts import redirect, render
# Models
import Cart.models as md
# Encryption
import bcrypt

def log_query():
    '''
    Logs query and query execution time 
    into "log.txt" file
    Last modified: 11/02
    '''
    f = open("log.txt", "a")
    for d in connections['data'].queries:
        f.write(str(d))
        f.write("\n")
    f.close()
    reset_queries()

def account(request):
    '''
    Handles account page
    Last modified: 10/07
    '''
    # Check if logged in
    if request.session.get('logged_in', False): 
        return redirect('index')
    # If not logged in, show account page
    else: 
        return render(request, "Cart/account.html", {})

def createAccount(request):
    '''
    Handles account creation
    Last modified: 11/02
    '''
    # Get form data from POST
    post_data = request.POST

    fName = post_data.get('firstName').strip().capitalize()
    lName = post_data.get('lastName').strip().capitalize()
    address = post_data.get('address')
    email = post_data.get('email').strip()
    phone = post_data.get('phone')
    password = post_data.get('password').strip()
    
    # Encrpt password
    bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(bytes, salt)

    # Create Customer object with form data
    c = md.Customer(first_name=fName, last_name=lName, address=address, email=email, phone=phone, password=hash)
    # Save newly created Customer object
    c.save(using='data')

    log_query()

    return redirect('login')

def login(request):
    '''
    Handles login page
    Last modified: 11/02
    '''
    # Check if logged in already
    if request.session.get('logged_in', False):
        return redirect('index')
    # Process form data if POST
    elif request.method == 'POST':
        post_data = request.POST
        email = post_data.get("email").strip()
        password = post_data.get("password").strip().encode('utf-8')

        # Check if user exists
        if md.Customer.objects.using('data').filter(email=email).exists():
            customer = md.Customer.objects.using('data').get(email=email)
            
            if bcrypt.checkpw(password, customer.password):
                request.session['logged_in'] = True
                request.session['member'] = customer.email
                return redirect('index')
            else: return render(request, "Cart/login.html", {'login_error': True})
        else: return render(request, "Cart/login.html", {'login_error': True})
    else: # Display login page
        return render(request, "Cart/login.html", {})

def logout(request):
    '''
    Handles loggin out
    Last modified: 11/02
    '''
    # Removing session information regarding logged in member
    if request.session.get('logged_in', False):
        request.session['member'] = None
        request.session['logged_in'] = False
    # Go to Login page
    return redirect('login')

def index(request):
    '''
    Handles index (i.e. home) page
    Last modified: 11/02
    '''
    # Check if logged in
    if request.session.get('logged_in', False):
        # Retrieve GET data
        num = request.GET.get('page', 1)
        by = request.GET.get('by', 'title')
        search = request.GET.get('search', None)

        # Retrieve user cart items
        cart_items = md.Book.objects.using('data').filter(
            cart__customer_id = request.session.get('member')
        )

        # Retrieve all books, exclude books already in cart
        if search is None: 
            url_query = "by={}".format(by)
            data = md.Book.objects.using('data').all().order_by(by if by != 'publisher' else 'publisher__name').exclude(isbn__in = cart_items)
        # Retrieve books based on search query, exlude books already in cart
        else: 
            url_query = "search={}".format(search)
            q1 = Q(title__icontains=search)
            q2 = Q(author__name__icontains=search)
            q3 = Q(publisher__name__icontains=search)
            data = md.Book.objects.using('data').filter(q1 | q2 | q3).exclude(isbn__in = cart_items).order_by('title')

        # Crate Paginator for page navigation
        p = Paginator(data, 60)
        page = p.page(num)

        log_query()

        return render(request, "Cart/index.html",
            {
                'title': "Books",
                'books': page,
                'url_query': url_query
            }
        )
    else: # If not logged in, redirect to login page
        return redirect('login')

def cart(request):
    '''
    Handles cart page
    Last modified: 11/02
    '''
    # Check if logged in
    if request.session.get('logged_in', False):
        # Retrieve cart items
        email = request.session.get('member')
        cart_items = md.Book.objects.using('data').filter(cart__customer_id=email)
        #cart_items = list(md.Cart.objects.using('data').filter(customer_id=email))

        q_result = cart_items.aggregate(Sum('price'))
        total = q_result['price__sum']

        log_query()

        # Display cart page with cart items
        return render(request, "Cart/cart.html", {"items": cart_items, "total": total})

    else: # If not logged in, redirect to login page
        return redirect('login')

def addCartItem(request):
    '''
    Adds selected item to cart
    Redirects to cart page
    Last modified: 11/02
    '''
    # Retrieve isbn for book to add to cart
    isbn = request.POST.get('isbn')

    book = md.Book.objects.using('data').get(isbn=isbn)

    email = request.session.get('member')
    item = md.Cart(book=book, customer_id=email)
    item.save(using='data') # Save book to cart

    log_query()

    return redirect('cart') # Reload cart page

def removeCartItem(request):
    '''
    Removes selected item to cart
    Redirects to cart page
    Last modified: 11/02
    '''
    # Retrieve isbn for book to remove from cart 
    isbn = request.POST.get('isbn')
    book = md.Cart.objects.using('data').get(book_id=isbn)
    book.delete() # Remove book from cart

    log_query()

    return redirect('cart') # Reload cart page

def purchase(request):
    '''
    Simulates purchase of items by
    removing books from cart and
    decrementing available stock 
    of each book purchased
    Last modified: 11/22
    '''
    if request.session.get('logged_in', False):
        # Retrieve cart items
        email = request.session.get('member')
        cart_items = md.Book.objects.using('data').filter(cart__customer_id=email)

        for b in cart_items:
            b.stock -= 1
            b.save()
        
        md.Cart.objects.using('data').filter(customer_id=email).delete() 

        log_query()

        # Return to home page
        return redirect('index')

    else: # If not logged in, redirect to login page
        return redirect('login')

def publisher(request, p=None):
    '''
    Handles publisher page
    Last modified: 11/02
    '''
    # Check if logged in
    if request.session.get('logged_in', False) and p != None:
        # Retrieve publisher information
        p_info = md.Publisher.objects.using('data').get(name=p)

        log_query()

        # Display page with publisher information
        return render(request, "Cart/publisher.html", {'publisher': p_info})

    else: # If not logged in, redirect to login page
        return redirect('login')

def author(request, a=None):
    '''
    Handles author page
    Last modified: 11/02
    '''
    # Check if logged in
    if request.session.get('logged_in', False) and a != None:
        a_info = md.Author.objects.using('data').get(name=a)

        log_query()

        # Display page with author information
        return render(request, "Cart/author.html", {'author': a_info})
    
    else: # If not logged in, redirect to login page
        return redirect('login') 
    
def about(request): 
    '''
    Handles about page
    Last modified: 09/26
    '''
    return render(request, "Cart/about.html",
        {
            'title': "About Cart",
            'content': "This is a project for CSCE5350: Database Systems"
        }
    )