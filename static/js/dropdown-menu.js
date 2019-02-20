$(function() {
  let collections = [];
  $('.collection-menu').on('mouseover', function() {
    $('.collection-list').html('');
    if (!collections.length) {
      $.get('/collections', function(response) {
        collections = response.collections;
        collections.forEach(function(collection_id){
          $('.collection-list').append('<li class="collection-item"><a href="">Collection' + collection_id + '</a><ul class="collection-detail"></ul></li>');
        });
      });
    } else {
      collections.forEach(function(collection_id){
        $('.collection-list').append('<li class="collection-item"><a href="">Collection' + collection_id + '</a><ul class="collection-detail"></ul></li>');
      });
    }
  });

  $('.collection-list-container').on('mouseleave', function() {
    $('.collection-list').html('');
  });

  $('.collection-list').on('mouseenter', '.collection-item', function(evt) {
    const $collectionDetail = $(this).find('ul.collection-detail');
    $collectionDetail.append('<li>item1</li><li>item2</li>');
  });

  $('.collection-list').on('mouseleave', '.collection-item', function(evt) {
    const $this = $(this);
    $this.find('ul.collection-detail').html('');
  });

});
