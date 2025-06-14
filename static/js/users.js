$(function(){
    function updateToolbar(){
        const anySelected = $('.select-user:checked').length > 0;
        $('#export,#edit,#audit,#transfer,#delete').prop('disabled', !anySelected);
    }
    $('.select-user').on('change', updateToolbar);

    $('.enable-toggle').on('change', function(){
        const row = $(this).closest('tr');
        const userId = row.data('user-id');
        const enabled = $(this).is(':checked');
        $.ajax({
            url: '/api/users/' + userId + (enabled ? '/enable' : '/disable'),
            method: 'PUT'
        });
    });

    $('#export').on('click', function(){
        window.location = '/export/users';
    });

    $('#create').on('click', function(){
        $('#create-modal').show();
    });
    $('#close-modal').on('click', function(){
        $('#create-modal').hide();
    });
});
