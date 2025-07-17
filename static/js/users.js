$(function(){
    // Populate group dropdowns from enabled groups
    $.getJSON('/api/user_groups?enabled=true', function(groups){
        const filter = $('#group-filter').empty();
        filter.append('<option value="all">All Groups</option>');
        groups.forEach(g => {
            const opt = $('<option>').val(g.name).text(g.name);
            if(filter.data('selected') === g.name) opt.attr('selected', 'selected');
            filter.append(opt);
            $('#new-group, #edit-group').append($('<option>').val(g.name).text(g.name));
        });
    });
    function updateToolbar(){
        const anySelected = $('.select-user:checked').length > 0;
        $('#export,#edit,#audit,#transfer,#delete').prop('disabled', !anySelected);
    }
    $('.select-user').on('change', updateToolbar);
    updateToolbar();

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
        window.location = '/api/users/export';
    });

    function selectedIds(){
        return $('.select-user:checked').closest('tr').map(function(){
            return $(this).data('user-id');
        }).get();
    }

    $('#create').on('click', function(){
        $('#create-modal').show();
    });
    $('#create-cancel').on('click', function(){
        $('#create-modal').hide();
    });
    $('#save-user').on('click', function(){
        const data = {
            name: $('#new-name').val(),
            principal_name: $('#new-principal').val(),
            role: $('#new-role').val(),
            email: $('#new-email').val(),
            group: $('#new-group').val(),
            password: $('#new-password').val(),
            enabled: $('#new-enabled').is(':checked')
        };
        $.ajax({
            url: '/api/users',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data)
        }).done(function(){ location.reload(); });
    });

    $('#edit').on('click', function(){
        const id = selectedIds()[0];
        const row = $('tr[data-user-id='+id+']');
        $('#edit-name').val(row.find('td').eq(1).text());
        $('#edit-principal').val(row.find('td').eq(2).text());
        $('#edit-role').val(row.find('td').eq(3).text());
        $('#edit-email').val(row.find('td').eq(4).text());
        $('#edit-group').val(row.find('td').eq(5).text().trim());
        $('#edit-enabled').prop('checked', row.find('.enable-toggle').is(':checked'));
        $('#edit-modal').data('user-id', id).show();
    });
    $('#edit-cancel').on('click', function(){
        $('#edit-modal').hide();
    });
    $('#save-edit').on('click', function(){
        const id = $('#edit-modal').data('user-id');
        const data = {
            name: $('#edit-name').val(),
            principal_name: $('#edit-principal').val(),
            role: $('#edit-role').val(),
            email: $('#edit-email').val(),
            group: $('#edit-group').val(),
            enabled: $('#edit-enabled').is(':checked')
        };
        $.ajax({
            url: '/api/users/'+id,
            method: 'PUT',
            contentType: 'application/json',
            data: JSON.stringify(data)
        }).done(function(){ location.reload(); });
    });

    $('#delete').on('click', function(){
        if(!confirm('Delete selected users?')) return;
        const ids = selectedIds();
        function del(i){
            if(i>=ids.length) { location.reload(); return; }
            $.ajax({ url: '/api/users/'+ids[i], method: 'DELETE'}).always(function(){ del(i+1); });
        }
        del(0);
    });

    $('#audit').on('click', function(){
        const id = selectedIds()[0];
        $.getJSON('/api/users/'+id+'/audit', function(logs){
            const list = $('#audit-list').empty();
            logs.forEach(l => list.append('<li>'+l.timestamp+': '+l.action+'</li>'));
            $('#audit-modal').show();
        });
    });
    $('#audit-close').on('click', function(){ $('#audit-modal').hide(); });

    $('#transfer').on('click', function(){
        const id = selectedIds()[0];
        $('#transfer-modal').data('user-id', id).show();
        // populate user options
        $.getJSON('/api/users', function(users){
            const select = $('#transfer-target').empty();
            users.forEach(u => { if(u.id!=id) select.append('<option value="'+u.id+'">'+u.name+'</option>'); });
        });
    });
    $('#transfer-cancel').on('click', function(){ $('#transfer-modal').hide(); });
    $('#transfer-confirm').on('click', function(){
        const id = $('#transfer-modal').data('user-id');
        const target = $('#transfer-target').val();
        $.ajax({
            url: '/api/users/'+id+'/transfer',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({target_id: target})
        }).done(function(){ alert('Transferred'); location.reload(); });
    });

    $('#find').on('click', function(){
        const role = $('#role-filter').val();
        const group = $('#group-filter').val();
        const params = new URLSearchParams();
        if(role && role !== 'all') params.append('role', role);
        if(group && group !== 'all') params.append('group', group);
        window.location = '/users' + (params.toString() ? '?'+params.toString() : '');
    });
});
