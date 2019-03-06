$(function() {
  const $shareBtn = $('.share-btn');
  const shareBtnData = $shareBtn.data('collection-id');

  $('.share-btn').on('click', function() {
    const data = {
      'collection_id': shareBtnData
    };

    $.get('/create_sharable_slug_collection', data, function(response) {
      const sharableLink = location.origin + '/c/' + response;
      $('.sharable-link__textbox').val(sharableLink);
      $('.sharable-link__background-drop').css('display', 'flex');
      $('.sharable-link__box-container').css('display', 'inline-block');
    });
  });

  $('.sharable-link__close-btn').on('click', function() {
    $('.sharable-link__background-drop').css('display', 'none');
  });
});
