"""Built-in prompt templates bundled with swiftstack-core."""

BLOG = """\
Build a Blog API with:

1. **User**
   - name, email, bio, role
   - hasMany: Posts

2. **Post**
   - title, content, status, publishedAt
   - belongsTo: User
   - hasMany: Comments

3. **Comment**
   - body, createdAt
   - belongsTo: Post, User
"""

ECOMMERCE = """\
Build an E-Commerce API with:

1. **Product**
   - name, description, price, stock, sku
   - belongsTo: Category

2. **Order**
   - status, totalAmount, shippingAddress
   - belongsTo: User
   - hasMany: OrderItems

3. **OrderItem**
   - quantity, unitPrice
   - belongsTo: Order, Product
"""

TASKMANAGER = """\
Build a Task Management API with:

1. **Project**
   - name, description, status, dueDate
   - belongsTo: User

2. **Task**
   - title, description, status, priority, dueDate
   - belongsTo: Project, User

3. **Comment**
   - body, createdAt
   - belongsTo: Task, User
"""

ALL = {
    "blog": BLOG,
    "ecommerce": ECOMMERCE,
    "taskmanager": TASKMANAGER,
}
