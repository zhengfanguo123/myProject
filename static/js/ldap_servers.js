$(function(){
    function updateToolbar(){
        const anySelected = $('.select-server:checked').length > 0;
        $('#edit-ldap,#audit-ldap,#delete-ldap').prop('disabled', !anySelected);
    }
    $('.select-server').on('change', updateToolbar);
    updateToolbar();

    function selectedId(){
        return $('.select-server:checked').first().closest('tr').data('server-id');
    }

    $('#edit-ldap').on('click', function(){
        const id = selectedId();
        if(id) window.location = '/wm/edit_ldapserver/' + id;
    });

    $('#delete-ldap').on('click', function(){
        const id = selectedId();
        if(!id || !confirm('Delete this LDAP server?')) return;
        $.ajax({url:'/api/ldap_servers/'+id, method:'DELETE'}).done(function(){ location.reload(); });
    });

    $('#audit-ldap').on('click', function(){
        const id = selectedId();
        $.getJSON('/api/ldap_servers/'+id+'/audit_log', function(logs){
            const list = $('#ldap-audit-list').empty();
            logs.forEach(l => list.append('<li>'+l.timestamp+': '+l.action+'</li>'));
            $('#ldap-audit-modal').show();
        });
    });
    $('#ldap-audit-close').on('click', function(){ $('#ldap-audit-modal').hide(); });
});

