# MML
A minimalistic replacement for XML inspired by [Jade](https://github.com/dscape/jade)

It looks like this:
```shell
!docType(html)
html(lang='en-US')
  head
    title Page Title
    script(type="text/javascript") """
      if (foo) bar(1+3)
    """
    # ignore me
  body
    h1 Hello, I'm a title
    p '''Hey
       this is a multi line text'''
```

Which translates to:
```html
<!docType html />
<html lang='en-US'>
  <head>
    <title>Page Title</title>
    <script type="text/javascript">
      if (foo) bar(1+3)
    </script>
    <!-- ignore me -->
  </head>
  <body>
    <h1>Hello, I'm a title</h1>
    <p>Hey
     this is a multi line text</p>
  </body>
</html>
  
```
