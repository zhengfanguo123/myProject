$(function(){
    function updateToolbar(){
        const anySelected = $('.select-role:checked').length > 0;
        $('#edit-role,#audit-role,#delete-role').prop('disabled', !anySelected);
    }
    $('.select-role').on('change', updateToolbar);
    updateToolbar();

    function selectedId(){
        return $('.select-role:checked').first().closest('tr').data('role-id');
    }

    $('#create-role').on('click', function(){
        $('#role-name').val('');
        $('#role-desc').val('');
        $('#role-perms').val('');
        $('#role-modal').data('role-id', '').show();
    });
    $('#role-cancel').on('click', function(){ $('#role-modal').hide(); });

    $('#role-save').on('click', function(){
        const id = $('#role-modal').data('role-id');
        const data = {
            name: $('#role-name').val(),
            description: $('#role-desc').val(),
            permissions: $('#role-perms').val().split(',').map(p=>p.trim()).filter(p=>p)
        };
        const url = id ? '/api/roles/'+id : '/api/roles';
        const method = id ? 'PUT' : 'POST';
        $.ajax({url:url,method:method,contentType:'application/json',data:JSON.stringify(data)})
            .done(function(){ location.reload(); });
    });

    $('#edit-role').on('click', function(){
        const id = selectedId();
        const row = $('tr[data-role-id='+id+']');
        $('#role-name').val(row.find('td').eq(1).text());
        $('#role-desc').val(row.find('td').eq(2).text());
        const perms = [];
        row.find('td').eq(3).find('.tag').each(function(){ perms.push($(this).text()); });
        $('#role-perms').val(perms.join(', '));
        $('#role-modal').data('role-id', id).show();
    });

    $('#delete-role').on('click', function(){
        const id = selectedId();
        if(!id || !confirm('Delete this role?')) return;
        $.ajax({url:'/api/roles/'+id, method:'DELETE'}).done(function(){ location.reload(); });
    });

    $('#audit-role').on('click', function(){
        const id = selectedId();
        $.getJSON('/api/roles/'+id+'/audit_log', function(logs){
            const list = $('#role-audit-list').empty();
            logs.forEach(l=>list.append('<li>'+l.timestamp+': '+l.action+'</li>'));
            $('#role-audit-modal').show();
        });
    });
    $('#role-audit-close').on('click', function(){ $('#role-audit-modal').hide(); });
});
