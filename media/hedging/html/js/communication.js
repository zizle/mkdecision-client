$(function () {
    // 请求数据填充
    $.ajax({
        url: host + 'delivery/questions/',
        type: 'get',
        success: function (res) {
            console.log(res);
            // 展示数据
            showContent(res.data)
        },
        error: function (res) {
            // console.log(res);
            showContent([], '查询记录失败.')

        }
    });
    // 搜索条目
    $('.search').on('click', 'button', function () {
        var keyword = $(this).prev('input').val();
        $.ajax({
            url: host + 'questions/?keyword=' + keyword,
            type: 'get',
            success: function (res) {
                // console.log(res)
                showContent(res)
            },
            error: function (res) {
                showContent([], "搜索失败.")
            }
        })
    });
    // 点击我的问题
    $('.myQuestion').on('click', 'a', function (e) {
        e.preventDefault();
        // 请求数据
        $.ajax({
            url: host + 'questions/?user=1',
            type: 'get',
            headers: {
                "Authorization": "JWT " + token
            },
            success: function (res) {
                showContent(res)
            },
            error: function (res) {
                if (res.status == 401){
                    showContent([], "您还没登录..")
                }else {
                    showContent([], "还没提问过，赶紧去提问吧...")
                }
            }
        })

    })

    var discussions = [
        {
            question:{
                questioner:{avatar:'media/boy.png', name:'李明'},
                content: '螺纹钢交割升贴水是怎么规定的？螺纹钢交割升贴水是怎么规定的？螺纹钢交割升贴水是怎么规定的？螺纹钢交割升贴水是怎么规定的？螺纹钢交割升贴水是怎么规定的？螺纹钢交割升贴水是怎么规定的？螺纹钢交割升贴水是怎么规定的？螺纹钢交割升贴水是怎么规定的？螺纹钢交割升贴水是怎么规定的？',
                create_time: '2019-09-04 12:24:20',
            },
            answers:[
                {
                    answerer:{avatar:'media/boy.png', name:'张三'},
                    content:'天津地区仓库交割贴水90元，江苏徐州地区仓库交割贴水70元。',
                    create_time: '2019-09-04 13:14:52'
                },
                {
                    answerer:{avatar:'media/girl.png', name:'李柒'},
                    content:'为啥这两个仓库会设有贴水？',
                    create_time: '2019-09-04 13:14:52'
                },
                {
                    answerer:{avatar:'media/boy.png', name:'张三'},
                    content:'您好！这个是上期所为了降低买方从产区运到销区的物流成本。',
                    create_time: '2019-09-04 13:14:52'
                },
                {
                    answerer:{avatar:'media/girl.png', name:'李柒'},
                    content:'谢谢！',
                    create_time: '2019-09-04 13:14:52'
                }
            ]
        },{
            question:{
                questioner:{avatar:'media/boy.png', name:'赵六'},
                content: '期货公司做原油交割需要具备什么样的条件？',
                create_time: '2019-09-04 12:24:20',
            },
            answers:[
                {
                    answerer:{avatar:'media/boy.png', name:'张三'},
                    content:'必须是能够开具或者接收上海国际能源交易中心规定发票人的企业法人。境内机构在首次申报原油期货报税交割业务免税时，应向主管税务机关提交从事原油期货保税交割业务的书面证明，办理免税备案并购买可供开具的增值税普通发票。',
                    create_time: '2019-09-04 13:14:52'
                }

            ]

        }
    ];

    // showContent(discussions);

    // 点击条目显示回答详情
    $('.communication').on('click', '.question', function () {
        $(this).next().toggle('fast');
        $(this).parent().siblings().children('.question').next().slideUp('fast')

    });
    // 初始点击[全部]分类按钮
    $('.activeLi').click();

    // 弹窗回答问题
    $('.communication').on('click', '.iAnswer', function (e) {
        e.stopPropagation();  // 阻止时间冒泡触发父点击事件
        // 获取问题详情
        var q = $(this).prev().html();
        var questionId = $(this).next('input').val();
        var qidEle = "<input type='hidden' value="+ questionId+">";
        $('.cover').show();
        $('.answerQuestion .questionDetail').html(q);
        $('.answerQuestion .questionDetail').append(qidEle);
        $('.answerQuestion').show();
    });

    // 弹窗显示发布问题
    $('.ask').on('click', 'a', function () {
        $('.cover').show();
        $('.askQuestion').show();
    });
    // 关闭弹窗
    $('.header').on('click', 'span', function () {
        $('.cover').hide();
        $('.askQuestion').hide();
        $('.answerQuestion').hide();
        $('.noAnswerSkip, .noQuestionSkip').hide();
    });
    // 发布问题
    $('.askQuestion').submit(function (e) {
        e.preventDefault();
        var ques = $.trim($('#textInput').val());
        if (!ques){
            $('.noQuestionSkip').html('请填写您的问题描述.');
            $('.noQuestionSkip').css('display', 'block');
            return
        }
        if (typeof (token) == "undefined"){
            $('.noQuestionSkip').html('请登录后进行操作.');
            $('.noQuestionSkip').css('display', 'block');
            return
        }
        // 发布问题
        $.ajax({
            url: host + 'delivery/questions/',
            type: 'post',
            contentType: 'application/json',
            data: JSON.stringify({
                content: ques,
            }),
            headers: {
                "AUTHORIZATION": token
            },
            success: function (res) {
                // console.log(res)
                location.reload();
            },
            error: function (res) {
                if (res.status == 400){
                    $('.noQuestionSkip').html(res.responseText);
                    $('.noQuestionSkip').css('display', 'block');
                }
            }
        });
        // location.reload();
    });
    // 发布回答
    $('.answerQuestion').submit(function (e) {
        e.preventDefault();
        var ans = $.trim($('#answerInput').val());
        var questionId = $('.answerQuestion .questionDetail').children('input').val();
        if (!ans){
            $('.noAnswerSkip').html('请编辑您的答案.');
            $('.noAnswerSkip').css('display', 'block');
            return
        }
        if (typeof (token) == "undefined"){
            $('.noAnswerSkip').html('请登录后进行操作.');
            $('.noAnswerSkip').css('display', 'block');
            return
        }
        // 发布回答
        $.ajax({
            url: host + 'answer/',
            type: 'post',
            contentType: 'application/json',
            data: JSON.stringify({
                content: ans,
                question_id: questionId,
            }),
            headers: {
                "Authorization": "JWT " + token
            },
            success: function (res) {
                console.log(res)
                // 关闭对话框
                $('.header').click();
                location.reload()
            },
            error: function (res) {
                if (res.status == 400){
                    $('.noAnswerSkip').html(res.responseText);
                    $('.noAnswerSkip').css('display', 'block');
                }
            }
        })
        // location.reload()
    });
    // 鼠标聚焦输入框
    $('#textInput').focus(function () {
        $('.noQuestionSkip').css('display', 'none');
    });
    $('#answerInput').focus(function () {
        $('.noAnswerSkip').css('display', 'none');
    })

});
function showContent(discussions, message='*没有相关的记录') {
    if (!discussions.length){
        $('.communication').html("<div class='noData'>"+message+"</div>");
        return
    }
    var communicationList = "";
    $('.unknowUser').hide();
    $.each(discussions, function (index, question) {
        var questionerAvatar = "media/boy.png";
        var questionerNickName = "未知用户";
        var questioner = question['questioner'];
        var answers = question['answers'];
        if (questioner){
            questionerAvatar=questioner['avatar'];
            questionerNickName=questioner['username'] || questioner['phone'];
        }else{
            $('.unknowUser').show();
        }
        var communicationItem = "<div class='communication-item'>";
        communicationItem += "<div class='question'>";
        communicationItem += "<div class='questionAuthor'><img src=" + questionerAvatar + " alt='头像'>&nbsp;&nbsp;"+ questionerNickName +"</div>";
        communicationItem += "<div class='question-title'>" + question['content']+ "</div>";
        communicationItem += "<div class='iAnswer'>我来回答</div><input type='hidden' value=" +question['id'] + ">";
        communicationItem += "<div class='question-date'>"+question['create_time']+"</div>";
        communicationItem += "<div class='question-reply'>回复: "+answers.length +"</div>";
        communicationItem += "</div>";
        // 遍历回答
        communicationItem += "<div class='answer'>";
        $.each(answers, function (answerIndex, answerItem) {
            var floorIndex = parseInt(answerIndex) + 1;
            var answerer = answerItem['answerer'];
            var answererAvatar = 'media/boy.png';
            var answererNickName = null;
            if (answerer){answererAvatar=answerer['avatar'];answererNickName=answerer['nick_name'] || answerer['username'].substring(0,4) + "****" + answerer['username'].substring(8,11)}
            communicationItem += "<div class='answerAuthor'><img src="+ answererAvatar +" alt='头像'>&nbsp;&nbsp;"+ answererNickName+"</div>";
            communicationItem += "<div class='answer-item'>";
            communicationItem += "<div class='answer-title'>"+answerItem['content']+"</div>";
            communicationItem += "<div class='answer-date'>"+answerItem['create_time']+"</div>";
            communicationItem += "<div class='answer-floor'>#"+floorIndex+"楼</div>";
            communicationItem += "</div>";

        });
        communicationItem += "</div>";
        communicationItem += "</div>";
        communicationList += communicationItem
    });
    $('.communication').html(communicationList)
}
