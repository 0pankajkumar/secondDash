        // Modify title
        document.title = "Modify Users";

        // Borrowed from https://stackoverflow.com/questions/42212964/delete-table-row-on-button-click-using-ajax
        $('.delete').click(function () {
            var button = $(this),
                tr = button.closest('tr');
            // find the ID stored in the .groupId cell
            //var id = tr.find('td.users').text();
            var id = $(this).closest('tr').find('.users').text();

            // your PHP script expects GROUP_ID so we need to pass it one
            var data = { users: id, actionType: "deleteUser" };

            // ask confirmation
            if (confirm('Are you sure you want to delete this entry?')) {
                // Deleting that row from website
                $(this).closest('tr').remove();
                
                // delete record only once user has confirmed
                $.post('/addDeleteModifyUser', data, function (res) {
                    
                    // we want to delete the table row only we received a response back saying that it worked
                    if (res.status) {
                        tr.remove();
                    }
                }, 'json');
            }
        });


        // Borrowed from https://stackoverflow.com/questions/42212964/delete-table-row-on-button-click-using-ajax
        $('.modify').click(function () {
            var button = $(this),
                tr = button.closest('tr');
            // find the ID stored in the .groupId cell
            //var id = tr.find('td.users').text();
            var id = $(this).closest('tr').find('.users').text();
            var typeData = $(this).closest('tr').find('.type').find(":selected").val();
            var tatMemberData = $(this).closest('tr').find('.tatMember').find(":selected").val();
            var whichPositionsData = $(this).closest('tr').find('.whichPositions').find(":selected").val();

            var data = { 
                users: id,
                typeData: typeData,
                tatMemberData: tatMemberData,
                whichPositionsData: whichPositionsData,
                actionType: "modifyUser"
            };


            // modify record
            $.post('/addDeleteModifyUser', data, function (res) {
                // we want to delete the table row only we received a response back saying that it worked
                if (res.status) {
                }
            }, 'json');
            
        });