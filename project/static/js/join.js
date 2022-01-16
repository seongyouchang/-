let now = new Date()
let year = now.getFullYear()

function birth() {
    let day = document.querySelector('#birth_input').value;
    console.log(day);
}

function selectEmail(ele) {
    let $ele = $(ele);
    let $email2 = $('input[name=email2]'); //email2에 적힌 값을 가져옴

    // '1'인 경우 직접입력
    if ($ele.val() == "1") {
        $email2.attr('readonly', false);
        $email2.val('');
    } else { //직접 입력이 아닌 경우
        $email2.attr('readonly', true);
        $email2.val($ele.val());
    }
}

function join_button() {
    if ($("#name_input").val().length == 0) {
        alert("이름을 입력하세요");
        $("#name_input").focus();
        return false;
    }
    else if ($("#birth_input").val().length == 0) {
        alert("생년월일을 입력하세요");
        $("#birth_input").focus();
        return false;
    }
    else if ($("#id_input").val().length == 0) {
        alert("아이디를 입력하세요");
        $("#id_input").focus();
        return false;
    }
    else if ($("#pwd_input").val().length == 0) {
        alert("비밀번호를 입력하세요");
        $("#pwd_input").focus();
        return false;
    }
    else if ($("#pwd_check").val().length == 0) {
        alert("비밀번호를 재확인 하세요");
        $("#pwd_check").focus();
        return false;
    }
    else if ($("#email1").val().length == 0) {
        alert("이메일을 입력하세요");
        $("#email1").focus();
        return false;
    }

    if ($("#pwd_input").val() != $("#pwd_check").val()) {
        alert("비밀번호가 일치 하지 않습니다");
        return false;
    }
    else if(year - $("#birth_input").val().split("-")[0] < 19){
        alert("19세 이상 가입이 가능합니다.\n 추후에 이용해주세요!")
         window.location.href = '/'
    }
    else { //비밀번호, 이메일 모두 정확할 경우
        let name = $('#name_input').val()
        let birth = $('#birth_input').val()
        let id = $('#id_input').val()
        let pw1 = $('#pwd_input').val()
        let email1 = $('#email1').val()
        let email2 = $('#email2').val()
        $.ajax({
            type: "POST",
            url: "/join",
            data: { name_give: name,
                    birth_give: birth,
                    id_give: id,
                    pw_give: pw1,
                    email_give: email1+"@"+email2
            },
            success: function (response) {
                if (response == true)   //회원가입성공
                {
                    alert("회원가입에 성공하였습니다!")
                    location.href = "/login";
                }
            }
        });
    }
}

function check() { // id 중복 체크
    let id = $('#id_input').val()
    $.ajax({
        type: "POST",
        url: "/id_check",
        data: {id_give: id},
        success: function (response) {
            if (response == true)   //중복되어 사용불가능한 아이디
            {
                alert("중복된 아이디입니다. 다시 입력해주세요")
                window.location.reload()
            } else    //사용가능한 아이디
            {
                alert("사용가능한 아이디입니다.")
            }
        }
    });

}