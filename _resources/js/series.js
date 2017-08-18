function toggle_visibility(dom_element_id){
  var element = document.getElementById(dom_element_id);

  element.style.display == 'none' ? element.style.display = '' : element.style.display = 'none';
}
