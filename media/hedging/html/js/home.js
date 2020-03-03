$(function () {
    // 如果有token,需要显示登录状态
    if (typeof (token) != "undefined"){
       $.ajax({
           url: host + "is_login/",
           type: 'get',
           headers:{
               "Authorization": "JWT " + token
           },
           success: function (res) {
               $('.passport button').hide();
               $('.passport em').html(res['nick_name'] || res['username'])
               $('.passport a').show();
               // 传出token到GUI界面
               sendTokenMessage(token)
           },
           error: function (res) {
           }
       })
    }
    // 请求新闻和公告数据展示(id和标题)
    $.ajax({
        url: host + 'newsbulletin/?scroll=1',
        type: 'get',
        success: function (res) {
            showNewsBulletin(res)

        },
        error: function (res) {
        }
    });
    // 新闻公告滚动
    setTimeout(function () {
        scrollDiv($(".newsList"));
    },1000);
    setTimeout(function () {
        scrollDiv($(".bulletinList"))
    }, 1000);
    // 点击滚动新闻条目
    $('.newsList, .bulletinList').on('click', 'li', function () {
        // console.log($(this).html());
        var article = $(this).data('article');
        var atype = $(this).data('atype');
        new QWebChannel(qt.webChannelTransport, function (channel) {
            // alert(parent_value)
            // alert([atype, article])
            var channelObj = channel.objects.messageChannel;
            channelObj.newsBulletinShow([atype, article])  // 通道对象信号槽函数
        });
    });
    // 点击“新闻”、“公告”显示列表
    $('.newsTitle, .bulletinTitle').on('click', 'span', function (e) {
        e.preventDefault();
        // alert('点击了新闻公告文字')
        new QWebChannel(qt.webChannelTransport, function (channel) {
            // alert(parent_value)
            // alert([atype, article])
            var channelObj = channel.objects.messageChannel;
            channelObj.newsBulletinShow(['get_list', 0])  // 通道对象信号槽函数
        });

    })
    // 获取交易所数据(品种,服务内容等)
    $.ajax({
        url: host + 'exchanges/',
        type: 'get',
        success: function (res) {
            // console.log(res);
            var varietyBlock = "";
            var serviceGuideBlock = "";
            $.each(res, function (eindx, exchange) {
                // 每一个交易所一个li标签
                varietyBlock += "<li>";
                serviceGuideBlock += "<li>";
                // 遍历交易所品种
                if (eindx == 0){
                    varietyBlock += "<span class='initExchange' data-value="+exchange.en_code+">"+ exchange.name +"</span>";
                    varietyBlock += "<ul class='belong-exchange' style='display: block;'>";
                    serviceGuideBlock += "<span class='initExchange' data-value="+exchange.en_code+">"+ exchange.name +"</span>";
                    serviceGuideBlock += "<ul class='belong-exchange hedging-guide' style='display: block;'>";
                }else{
                    varietyBlock += "<span data-value="+exchange.en_code+">"+ exchange.name +"</span>";
                    varietyBlock += "<ul class='belong-exchange'>";
                    serviceGuideBlock += "<span data-value="+exchange.en_code+">"+ exchange.name +"</span>";
                    serviceGuideBlock += "<ul class='belong-exchange hedging-guide'>";
                }
                $.each(exchange.varieties, function (vindx, variety) {
                    varietyBlock += "<li data-value="+variety.en_code+">" + variety.name+"</li>"
                });
                $.each(exchange.service_guides, function (sindx, guide) {
                    serviceGuideBlock += "<li data-value='"+guide.en_code+"'>"+guide.name+ "</li>"
                });

                varietyBlock += "</ul>";
                varietyBlock += "</li>";
                serviceGuideBlock += "</ul>";
                serviceGuideBlock += "</li>";
            });
            $('.variety-show').html(varietyBlock);
            $('.guide').html(serviceGuideBlock);
        },
        error: function (res) {
            alert("shibai ")
            console.log(res)
        }
    });
    // 获取地区
    $.ajax({
        url: host + 'areas/',
        type: 'get',
        success: function (res) {
            // console.log(res);
            var areaEle = "";
            var areaJson = {};
            $.each(res, function (aindx, area) {
                if (area.name.length > 3){
                    var areaName = area.short_name;
                }else{
                    var areaName = area.name;
                }
                areaEle += "<li data-value="+area.en_code+">" + areaName + "</li>";
                areaJson[area.short_name] = area.en_code;
            });
            $('.province-show').html(areaEle);
            localStorage.areaJson = JSON.stringify(areaJson);
        },
        error: function (res) {
            console.log(res)
        }
    });
    // 登录
    $('.passport').on('click', 'button', function () {
        $('.cover').show();
        $('.login').show();
    });
    // 关闭登录注册框
    $('.header').on('click', 'span', function () {
        $('.cover').hide();
        $('.login').hide();
        $('.login input').val('');
        $('.login p').html('&nbsp;')
    });
    // 登录注册切换
    $('.header').on('click', 'a', function () {
        if($(this).hasClass('.header-active')){
            return
        }
        $(this).attr('class', 'header-active');
        $(this).siblings('a').removeAttr('class');
        var index = $(this).index();
        if (!index){
            $('.login-box').show();
            $('.register-box').hide();
            $('.login').css('height', '240px')  // 直接设置高度，防止弹窗模糊
        }else{
            $('.register-box').show();
            $('.login-box').hide();
            $('.login').css('height', '477px');
            // 改变注册框内的图片验证码
            var imageUUID = generate_uuid();
            var imageCodeUrl = host + "image_codes/" + imageUUID + "/";
            $("#svryanzhenma").attr('src', imageCodeUrl);
            $("#svryanzhenma").attr('data-uuid', imageUUID);
        }
    });
    // 注册验证码点击事件
    $('#svryanzhenma').click(function () {
        $("#ryanzheng").val('');
        var imageUUID = generate_uuid();
        $("#svryanzhenma").attr('src', host + "image_codes/" + imageUUID + "/");
        $("#svryanzhenma").attr('data-uuid', imageUUID);
    });
    // 登录注册错误信息消失
    $('.login input').focus(function () {
        var $p = $(this).parent().next();
        $p.html('&nbsp;');
        $('.login-box').children(":first").html('&nbsp;')
        $('.register-box').children(":first").html('&nbsp;')
    });
    // 登录注册错误信息提示
    $('.login input').blur(function () {
        var inputId = $(this).attr('id');
        var inputVal = $(this).val();
        if (inputId == 'lmobile'){
            // 检测手机号规则
            if (!isPhoneNo(inputVal)){
                pShowTip($(this), '手机号格式有误.')
            }
        }else if (inputId == 'lpsd'){
            // 检测密码位数
            if (inputVal.length < 6){
                pShowTip($(this), '密码至少为6位数.')
            }
        }else if (inputId == 'rmobile'){
            // 检测手机号规则
            if (!isPhoneNo(inputVal)){
                pShowTip($(this), '手机号格式有误.')
            }
        }else if (inputId == 'rpsd1'){
            // 检测密码位数
            if (inputVal.length < 6){
                pShowTip($(this), '密码至少为6位数.')
            }
        }else if (inputId == 'rpsd2'){
            // 检测两次密码是否一致
            var psd1 = $('#rpsd1').val();
            var psd2 = $('#rpsd2').val();
            if (psd1 != psd2){
                pShowTip($(this), '两次输入的密码不一致.')
            }
        }else if (inputId == 'rusername') {
            var nickNamePassed = true;
            var registerName = $('#rusername').val();
            if (!registerName.length){
                pShowTip($(this), '用户名/昵称不能为空')
                nickNamePassed = false;
            } else if (registerName.length >10){
                pShowTip($(this), '用户名/昵称超过10个字符.');
                nickNamePassed = false;
            }
            if (nickNamePassed){
                // 用户名称存在请求
                var $thisInpt = $(this);
                $.ajax({
                    url: host + 'user_exist/?nick_name=' + registerName,
                    type:'get',
                    success: function (res) {
                        console.log(res.nick_name_passed, typeof (res.nick_name_passed));
                        if (!res.nick_name_passed) {
                            pShowTip($thisInpt, '当前用户名/昵称已存在.');
                        }
                    }
                })

            }
        }else if (inputId == 'ryanzheng'){
            var imageCode = $('#ryanzheng').val();
            if (!imageCode.length){
                pShowTip($(this), '请输入验证码.')
            }
        }
    });
    // 点击登录或者注册
    $('.loginBtn').click(function () {
        $('.login-box input').blur();
        if (isPassport($('.login-box p'))){
            var mobile = $('#lmobile').val();
            var psd = $('#lpsd').val();
            // console.log('发起登录请求', mobile, psd)
            $.ajax({
                url: host + 'login/',
                type: 'POST',
                data: JSON.stringify({
                    username: mobile,
                    password: psd
                }),
                contentType: 'application/json',
                dataType: "json",
                success: function (res) {
                    console.log(res);
                    // 登录成功
                    $('.passport button').hide();
                    $('.passport em').html(res['nick_name']|| res['username']);
                    $('.passport a').show();
                    $('.cover').hide();
                    $('.header span').click();
                    // 存入本地存储
                    localStorage.token = res['token'];
                    token = localStorage.token;
                    // 传出token到GUI界面
                    sendTokenMessage(localStorage.token)
                },
                error: function (res) {
                    // console.log(res);
                    if (res.status == 400){
                        $('.login-box').children(":first").html('用户名或密码错误.')
                    }
                }
            })

        };
    });
    $('.registerBtn').click(function () {
        $('.register-box input').blur();
        if (isPassport($('.register-box p'))){
            var nickName= $("#rusername").val();
            var phone = $("#rmobile").val();
            var psd1 = $("#rpsd1").val();
            var psd2 = $("#rpsd2").val();
            var imageCode = $("#ryanzheng").val();
            var imageUUID = $("#svryanzhenma").data('uuid');
            // console.log('发起注册请求')
            $.ajax({
                url:host + 'user/',
                type: 'POST',
                data: JSON.stringify({
                    phone: phone,
                    password1: psd1,
                    password2: psd2,
                    nick_name: nickName,
                    image_code: imageCode,
                    image_code_id: imageUUID,
                }),
                contentType: 'application/json',
                dataType: "json",
                success: function (res) {
                    console.log(res);
                    $('.register-box').children(':first').html('注册成功！赶紧去登录吧')
                    $('.login-box input').val('');
                    $('.login-box p').html('&nbsp;')
                },
                error: function (res) {
                    // 提示错误内容
                    console.log(res);
                    if (res.status == 400){
                        $('.register-box').children(":first").html(res.responseText)
                    }
                }
            });
        }
    });
    // 点击横向菜单显示菜单下的内容(主菜单)
    $('.nav').on('click', 'a', function () {
        var clickOption = $(this).data('category');
        if (clickOption == 'map'){
            $('#frame').attr('src', 'map.html');
            // 设置高度
            $('#frame').load(function () {
                $('#frame').css('height', $('#frame').contents().height() + 'px')
            })
        }else {
            var next = $(this).next();
            // next.css('display', 'block')
            next.toggle()
        }
        $(this).parent().siblings().children('.nav-show').hide();
    });
    // 悬浮交易所显示相应品种
    $('.nav-show').on('hover', 'span', function () {
        // $(this).css('color', '#000000');
        // $(this).css('font-weight', 'bold');
        $(this).attr('class', 'initExchange')
        var next = $(this).next();
        // next.css('display', 'block');
        next.show();
        // 其他交易所的隐藏
        $(this).parent().siblings().children('.belong-exchange').hide();
        // $(this).parent().siblings().children('span').css('color', '#696969');
        // $(this).parent().siblings().children('span').css('font-weight', 'normal');
        $(this).parent().siblings().children('span').removeAttr('class')

    });
    // 点击品种的子菜单选项
    $('.variety-show').on('click', 'li', function (e) {
        var whichExchange = $(this).parent().prev().data('value');
        var current_variety = $(this).data('value');
        if (typeof (whichExchange)=="undefined" || typeof (current_variety) == "undefined"){return false}
        $('.nav-show').slideUp('fast');
        $('#frame').attr('src', 'variety.html?exchange=' + whichExchange + '&selected=' + current_variety);
        // 设置高度
        // reinitIframe();
        // // $('#frame').css('height', $('#frame').contents().height() + 100 + 'px')
        // console.log($('#frame').contents().height())
        // $('#frame').load(function () {
        //     $('#frame').height = 0;
        //     $('#frame').css('height', $('#frame').contents().height() + 100 + 'px')
        // })
    });
    // 点击地区的省份
    $('.province-show').on('click', 'li', function () {
       $('.nav-show').slideUp('fast');
        var current_province = $(this).data('value');  // 当前省份
        $('#frame').attr('src', 'province.html?province=' + current_province);
        // reinitIframe()
        // // 设置高度
        // $('#frame').load(function () {
        //     $('#frame').css('height', $('#frame').contents().height() + 100 + 'px')
        // })
    });
    // 点击服务指引
    $('.guide').on('click', 'li', function () {
        var whichExchange = $(this).parent().prev().data('value');
        var current_service = $(this).data('value');
        if (typeof (whichExchange)=="undefined" || typeof (current_service) == "undefined"){return false}
        // 传出信号到界面
        new QWebChannel(qt.webChannelTransport, function (channel) {
            var channelObj = channel.objects.messageChannel;
            channelObj.serviceGuide([whichExchange, current_service]);  // 通道对象信号槽函数
        });

    });
    // 最新讨论交流
    $.ajax({
        url: host + 'questions/',
        type: 'get',
        success: function (res) {
            // console.log(res);
            showLastedQuestion(res)
        },
        error: function (res) {
            console.log(res);
            showLastedQuestion([])
        }
    });
    // 讨论交流展开
    $('.communication').on('click', '.question', function () {
        $(this).next().toggle('fast');
        $(this).parent().siblings().children('.question').next().slideUp('fast')
    });
    // 点击讨论交流的[更多]传出信号,新跳页面
    $('.communication').on('click', 'a', function () {
        new QWebChannel(qt.webChannelTransport, function (channel) {
            // alert(parent_value);
            var channelObj = channel.objects.messageChannel;
            channelObj.moreCommunication(true);  // 通道对象信号槽函数
        });
    });
    // 品种模式frame内请求文件转化为这里的点击事件
    $('#varietyBaseFile').click(function (e) {
        e.preventDefault();
        var fileUrl = $(this).children("input").val();
        console.log(fileUrl);
        new QWebChannel(qt.webChannelTransport, function (channel) {
            var channelObj = channel.objects.messageChannel;
            channelObj.fileUrlMessage(fileUrl);  // 通道对象信号槽函数
        });
        $(this).children("input").val('');
    });
    // 初始化显示中国地图
    $('.map').click();

    // 搜索
    $('.navSearch').on('click', 'button', function () {
        // frame加载地图页
        var keyword = $(this).prev('input').val();
        $("#frame")[0].contentWindow.reloadMap(keyword);  // 调用iframe页面里的函数
        // $('.map').click();
    })
    // 各许可协议点击
    $('.agree').on('click', 'a', function (e) {
        e.preventDefault();
        // 请求协议的内容
        var licenseName = $.trim($(this).html());
        var licenseContent = "<div class='licenseHeader'><div class='licenseName'>"+licenseName+"</div>";
        licenseContent += "<span>关闭</span> </div>";
        $(".license").html(licenseContent)
        $.ajax({
            url: host + 'license/?licenseName=' + licenseName,
            type: 'get',
            success: function (res) {
                $(".license").append(res)
            },
            error: function (res) {

            }
        });

        $('.license').show();

    });
    // 关闭协议
    $('.license').on('click', 'span', function () {
        $('.license').hide();
    })
});

function scrollDiv($div) {
    var wrap = $div;
    var ulEle = wrap.find('ul');
    var wrapWidth = wrap.width();
    var timer = null;
    var liWidth = 0;

    ulEle.find('li').each(function () {
        liWidth += $(this).outerWidth();

    });
    // console.log(liWidth, wrapWidth)
    if (liWidth <= wrapWidth){
        return false;
    }

    ulEle.css('width', liWidth);
    var i = 0;
    var x = 0;
    function _marquee() {
        var _w = ulEle.find('li:eq(0)').outerWidth();
        i ++;
        if (i >= _w) {
            ulEle.find('li:eq(0)').remove();
            i = 0;
            x = 0;
        }else {
            ulEle.find('li:eq(0)').css('marginLeft', -i);  // 改变margin至左就会超出隐藏
            if (i >= Math.max(_w - wrapWidth, 0)) {
                if (x === 0) {
                    var _li = ulEle.find('li:eq(0)').clone(true);
                    ulEle.append(_li.css('paddingLeft', 10));  // 间距。设置与改变的不一样就不会有跳动视觉，流畅
                    x = 1;
                }
            }
        }
        var _ul_w = 0;
        ulEle.find('li').each(function () {
            _ul_w += $(this).outerWidth();
        });
        ulEle.css('width', _ul_w);
    }
    timer = setInterval(_marquee, 30);
    $div.on('mouseover', function () {
        clearInterval(timer)
    });
    $div.on('mouseleave', function () {
        timer = setInterval(_marquee, 30);
    });
}

// 验证手机号
function isPhoneNo(phone) {
 var pattern = /^1[34578]\d{9}$/;
 return pattern.test(phone);
}

// p标签显示错误信息
function pShowTip($inp, tip) {
    var $p = $inp.parent().next();
    $p.html(tip);
}
// 遍历p标签判断是否有错误信息
function isPassport($pList) {
    var error = null;
    $pList.each(function () {
        if($(this).html() != '&nbsp;'){
            error = false;
            return false;
        }
    });
    if (error != null){
        return error;
    }else{
        return true;
    }
}

// 用户注销
function userLogout() {
    // 清除浏览器保存信息
    localStorage.clear();
    $('.passport em').html('');
    $('.passport a').hide();
    $('.passport button').show();
}

// 展示最新讨论数据
function showLastedQuestion(questions) {
    var firstEle = $('.communication').children(':first');
    $('.communication').html('');
    $('.communication').append(firstEle);
    if (!questions.length){
        var noData = "<div class='noData'>*暂无数据</div>";
        $('.communication').append(noData);
    }
    var communicationList = "";
    $.each(questions, function (qindx, question) {
        var answers = question['answers'];
        var communicationElem = "<div class='communication-item'>";
        communicationElem += "<div class='question'>";
        communicationElem += "<div class='question-title'>"+question['content']+"</div>";
        communicationElem += "<div class='question-date'>"+ question['create_time']+"</div>";
        communicationElem += "<div class='question-reply'>回复:"+answers.length+"</div>";
        communicationElem += "</div>";
        // 问题的答案
        communicationElem += "<div class='answer'>";
        $.each(answers, function (aindx, answer) {
            var floor = aindx + 1;
            var answerer = answer['answerer'];
            var answererNickName = '未知'
            if (answerer){
                answererNickName = answerer['nick_name'] || answerer['username']
            }
            communicationElem += "<div class='answerAuthor'><img src="+answerer['avatar']+" alt='头像'>&nbsp;&nbsp;"+answererNickName+"</div>";
            communicationElem += "<div class='answer-item'>";
            communicationElem += "<div class='answer-title'>"+answer['content']+"</div>";
            communicationElem += "<div class='answer-date'>"+answer['create_time']+"</div>";
            communicationElem += "<div class='answer-floor'>#"+floor+"楼</div>";
            communicationElem += "</div>" ;
        });
        communicationElem += "</div>";
        communicationElem += "</div>";
        communicationList += communicationElem;
        if (qindx == 4){  // 控制显示的条数
            return false
        }
    });
    $('.communication').append(communicationList)
    // 轮询设置页面高度
    window.setInterval("reinitIframe()", 300)
}

// 传token到GUI界面
function sendTokenMessage(token_string) {
    new QWebChannel(qt.webChannelTransport, function (channel) {
        var channelObj = channel.objects.messageChannel;
        channelObj.userTokenMessage(token_string);  // 通道对象信号槽函数
    });
}

// 填充新闻公告
function showNewsBulletin(newsBulletin) {
    var newContent = "<ul>";
    $.each(newsBulletin['news'], function (index, newsItem) {
        newContent += "<li data-atype='news' data-article=" + newsItem['id'] + ">" + newsItem['title'] + "</li>";
    });
    newContent += "</ul>";
    var bulletinContent = "<ul>";
    $.each(newsBulletin['bulletin'], function (index, bulletinItem) {
        bulletinContent += "<li data-atype='bulletin' data-article=" + bulletinItem['id'] + ">" + bulletinItem['title'] + "</li>";
    });
    bulletinContent += "</ul>";
    $('.newsList').html(newContent);
    $('.bulletinList').html(bulletinContent);
}

function reinitIframe(){

var iframe = document.getElementById("frame");

iframe.height = 0; //只有先设置原来的iframe高度为0，之前的iframe高度才不会对现在的设置有影响
try{
var bHeight = iframe.contentWindow.document.body.scrollHeight;
var dHeight = iframe.contentWindow.document.documentElement.scrollHeight;
var height = Math.max(bHeight, dHeight);
iframe.height = height;
$('#frame').css('height', height);
// console.log(height);
}catch (ex){}
}

// 生成图片验证码的uuid
function generate_uuid(){
    var d = new Date().getTime();
    if(window.performance && typeof window.performance.now === "function"){
        d += performance.now(); //use high-precision timer if available
    }
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = (d + Math.random()*16)%16 | 0;
        d = Math.floor(d/16);
        return (c =='x' ? r : (r&0x3|0x8)).toString(16);
    });
    return uuid;
}

