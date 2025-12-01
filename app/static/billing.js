function addProductRow(){
  idx += 1
  const container = document.getElementById('products_container')
  const div = document.createElement('div')
  div.className = 'product_row'
  div.innerHTML = `
    <select name="product_code_${idx}">
      <option value="">-- select --</option>
    </select>
    <input type="number" name="qty_${idx}" min="1" value="1">
  `
  const firstSelect = container.querySelector('select')
  const sel = div.querySelector('select')
  sel.innerHTML = firstSelect.innerHTML
  container.appendChild(div)
}
