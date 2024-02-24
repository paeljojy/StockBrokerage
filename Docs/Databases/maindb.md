# Database diagram
Copy paste this to [dbdiagram](https://dbdiagram.io/d)
(without ``` ``` obviously)

```

Table users {
  id integer [primary key]
  userkey varchar
  username varchar
  password varchar
  name varchar
  email varchar
  money integer
}

Table owned {
  user_id integer
  stock_id integer
  amount integer
}

Table stocks {
  id integer [primary key]
  title varchar
  current_value integer
  other_value integer
  other_info varchar
  updated datetime
}

Table bids {
  user_id integer
  stock_id integer
  amount integer
  price integer
}

Table offers {
  user_id integer
  stock_id integer
  amount integer
  price integer
}

Table trades {
  buyer_id integer
  seller_id integer
  stock_id integer
  time datetime
  amount integer
  price integer
}


Ref: users.id - owned.user_id

Ref: users.id - bids.user_id

Ref: users.id - offers.user_id

Ref: users.id - trades.buyer_id

Ref: users.id - trades.seller_id

Ref: stocks.id - owned.stock_id

Ref: stocks.id - bids.stock_id

Ref: stocks.id - offers.stock_id

Ref: stocks.id - trades.stock_id

```