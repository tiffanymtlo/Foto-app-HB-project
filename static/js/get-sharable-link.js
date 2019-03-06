$(function() {
  const $shareBtn = $('.share-btn');
  const shareBtnData = $shareBtn.data('person-ids');
  let idsInInt;
  if (typeof shareBtnData === 'number') {
    idsInInt = [shareBtnData];
  }
  else {
    const idsInString = shareBtnData.split('&');
    idsInInt = idsInString.map(function(idString) {
      return parseInt(idString, 10);
    });
  }

  $('.share-btn').on('click', function() {
    const data = {
      'person_ids': idsInInt
    };

    $.post('/share_photos', data, function(response) {
      const sharableLink = location.origin + '/p/' + response;
      $('.sharable-link__textbox').val(sharableLink);
      $('.sharable-link__background-drop').css('display', 'flex');
      $('.sharable-link__box-container').css('display', 'inline-block');
    });
  });

  $('.sharable-link__close-btn').on('click', function() {
    $('.sharable-link__background-drop').css('display', 'none');
  });
});
