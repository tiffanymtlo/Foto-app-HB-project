$(function() {
  let collectionInfoList;

  $('.collections-menu').hover(function() {
    const $this = $(this);
    const $collectionMenuContainer = $this.find('.collections-menu__collections');

    if (!collectionInfoList) {
      $.get('/collections', function(response) {
        collectionInfoList = response;

        if (response.length === 0) {
          const $emptycollection = $('<li>', {
            'class': 'collection',
            html: 'You have no collection to show.'
          });
          $collectionMenuContainer
            .html($emptycollection)
            .addClass('show');
        }
        else {
          const collectionItemsList = collectionInfoList.map(function(collection) {
            const $collectionLink = $('<a>', {
              'class': 'collection__link',
              href: '/collections/' + collection.id,
              html: 'Collection ' + collection.id
            });

            const $collectionDetails = $('<div>', {
              'class': 'collection__details',
              html: 'There are ' + collection.numPhotos + ' photos and ' + collection.numPersons + ' persons.'
            });

            const $collection = $('<li>', {
              'class': 'collection'
            });

            $collection
              .append($collectionLink)
              .append($collectionDetails);

            return $collection;
          });
          $collectionMenuContainer
            .html(collectionItemsList)
            .addClass('show');
        }
      });
    }
    else {
      $collectionMenuContainer
        .addClass('show');
    }
  },
  function() {
    const $this = $(this);
    $this.find('.collections-menu__collections').removeClass('show');
  });
});
