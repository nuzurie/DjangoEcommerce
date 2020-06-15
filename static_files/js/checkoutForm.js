
document.querySelector('#div_id_province').style.visibility = 'hidden'
document.querySelector('#div_id_ca_postal_code').style.visibility = 'hidden'
document.querySelector('#div_id_us_state').style.visibility = 'hidden'
document.querySelector('#div_id_us_zip_code').style.visibility = 'hidden'


function hide(id){
    toHide = document.querySelector('#'+id);
    toHide.style.visibility = 'hidden';
}

function show(id){
    toShow = document.querySelector('#'+id);
    toShow.style.visibility = 'visible';
}

function countrySelect(select){
    if (select.value === 'CA'){
        show('div_id_province');
        show('div_id_ca_postal_code');
        hide('div_id_us_state');
        hide('div_id_us_zip_code');
    }
    else if(select.value === 'US'){
        show('div_id_us_state');
        show('div_id_us_zip_code');
        hide('div_id_province');
        hide('div_id_ca_postal_code')
    }
    else{
        hide('div_id_us_state');
        hide('div_id_us_zip_code');
        hide('div_id_province');
        hide('div_id_ca_postal_code')
    }
}