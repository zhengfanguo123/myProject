$(function(){
    function updateToolbar(){
        const anySelected = $('.select-group:checked').length > 0;
        $('#edit-group,#audit-group,#delete-group').prop('disabled', !anySelected);
    }
    $('.select-group').on('change', updateToolbar);
    updateToolbar();

    $('.enable-toggle').on('change', function(){
        const row = $(this).closest('tr');
        const id = row.data('group-id');
        const enabled = $(this).is(':checked');
        $.ajax({
            url: '/api/user_groups/'+id,
            method: 'PUT',
            contentType: 'application/json',
            data: JSON.stringify({enabled: enabled})
        });
    });

    function selectedId(){
        return $('.select-group:checked').first().closest('tr').data('group-id');
    }

    $('#create-group').on('click', function(){
        $('#group-name').val('');
        $('#group-parent').val('');
        $('#group-enabled').prop('checked', true);
        $('#group-modal').data('group-id', '').show();
    });

    $('#edit-group').on('click', function(){
        const id = selectedId();
        const row = $('tr[data-group-id='+id+']');
        $('#group-name').val(row.find('td').eq(1).text());
        $('#group-parent').val(row.find('td').eq(2).text());
        $('#group-enabled').prop('checked', row.find('.enable-toggle').is(':checked'));
        $('#group-modal').data('group-id', id).show();
    });

    $('#group-cancel').on('click', function(){
        $('#group-modal').hide();
    });

    $('#group-save').on('click', function(){
        const id = $('#group-modal').data('group-id');
        const data = {
            name: $('#group-name').val(),
            parent_id: $('#group-parent').val() || null,
            enabled: $('#group-enabled').is(':checked')
        };
        const url = id ? '/api/user_groups/'+id : '/api/user_groups';
        const method = id ? 'PUT' : 'POST';
        $.ajax({
            url: url,
            method: method,
            contentType: 'application/json',
            data: JSON.stringify(data)
        }).done(function(){ location.reload(); });
    });

    $('#delete-group').on('click', function(){
        const id = selectedId();
        if(!id || !confirm('Delete this group?')) return;
        $.ajax({url:'/api/user_groups/'+id, method:'DELETE'})
            .done(function(){ location.reload(); });
    });

    $('#audit-group').on('click', function(){
        const id = selectedId();
        $.getJSON('/api/user_groups/'+id+'/audit_log', function(logs){
            const list = $('#group-audit-list').empty();
            logs.forEach(l => list.append('<li>'+l.timestamp+': '+l.action+'</li>'));
            $('#group-audit-modal').show();
        });
    });

    $('#group-audit-close').on('click', function(){
        $('#group-audit-modal').hide();
    });
});
