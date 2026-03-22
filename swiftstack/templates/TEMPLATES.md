# SwiftStack Templates

Ready-to-use prompt templates for common project types.
Copy any of these into the CLI or hosted API.

---

## 1. Blog API

```
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
```

---

## 2. E-Commerce API

```
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
```

---

## 3. Task Management API

```
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
```

---

> **Need more entities, relationships, or multi-framework output?**
> Use the hosted version: https://swiftstackapi.up.railway.app
