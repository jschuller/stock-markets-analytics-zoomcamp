0:41
hello everyone welcome to the stock markets analytics zoom zoom camp 2025
0:50
edition nice to see you all we'll wait for one more minute and
0:56
we will start
1:06
please write in the chat where are you from and let's greet each other
1:20
first of all I'd like to mention that any lectures uh and assignments that we
1:26
present uh it's not an investment advice uh you should use it for uh educational
1:33
purposes and not for your investment decisions first of all uh if you don't
1:40
know me I'm Ivan um I'm a business intelligence analyst at Google i also
1:46
have educational background in computer science finance and data analytics so a
1:51
little bit of everything i founded pythoninvest.com um four years ago where I regularly
1:59
write um articles and analytical stories about financial markets and uh um I do
2:09
invest my own money uh recently um I explore um
2:15
fundamental data and options trading so I write um about it as well uh I just
2:23
released an article about fundamental um data less than one months ago so you
2:31
might see uh new um additional features
2:36
um in in this stock markets uh analytics zoom camp
2:42
edition today we will um we will uh have
2:48
three um major topics one is uh the
2:53
first topic is a questionary update i will share um the stats that you already
2:59
see saw in um pre-launch um
3:04
uh video stream then we will um talk about making datadriven decisions i know
3:12
it can be quite challenging uh for u many of you to um dive into uh the area
3:22
of finance uh investing and economics and I've seen uh a lot of feedback that
3:29
I'm uh using uh many of jargon words that you might not understand but uh
3:36
it's quite hard to combine all all the knowledge uh in in five um lectures so I
3:45
assume that you can uh click uh the the links that I provide and read some
3:52
additional supplementary materials if you don't understand something so in in
3:57
this introductionary section we will talk about the philosophy of the data
4:02
informed decision making we will overview your potential
4:08
um investment opportunities and this data is updated from the last year we will um discuss what what changed in in
4:17
one year we will understand uh risk versus reward some metrics that you need
4:23
to choose um for yourself when you try to select an asset class or design your
4:29
trading strategy and then we will look at some of the real world uh data examples S&P 500 interest rates ETFs
4:40
um later uh we will talk about uh programming setup that's um in in most
4:46
of the lectures I will use collab um and um the collab code um is already shared
4:55
uh on on GitHub you can um open it you can try to execute it and uh uh you
5:03
should be able to replicate all the data that I I show you here in the
5:11
lectures um okay so um the question section uh is is
5:18
the same on slider.com um I I know that we haven't
5:24
answered some of the questions from the last Q&A session and we will do it today
5:30
but first uh there are a few questions from 2024 um that I believe are
5:37
important so question number one finance argues uh that prices reflect all
5:43
available information making it impossible to systematically beat the market how will you deal with with it in
5:50
the course of course uh we we are not providing some uh winning trading
5:57
strategy or always winning trading strategy but as you may notice that
6:02
there are many retail investors mutual funds hedge funds exist um in the market
6:07
and they regularly invest so hopefully we can um we can make some practice uh which
6:18
um delivers um positive results and the second uh thing is that we discuss the
6:25
the relative growth or uh growth versus benchmark so um each of you need to
6:31
define um what benchmark you have on a local market on a global market on an
6:36
asset class or your personal um aspirations and you can compare versus
6:44
um this benchmark whether your trading strategy is performing better or worse
6:50
question number two how much math do we need to know in order to succeed in the course i would say that um general
6:58
education math um the math is not very complicated um although if you want to
7:05
understand ML predictions better and uh go deeper into um ML modeling and
7:12
selecting more complicated um algorithms uh linear algebra probability theory and
7:20
statistics are useful question number three can you share the
7:25
description of the video some references for the theoretical concepts underlying
7:31
strategies uh again we we just do practical aspects
7:37
um every every time we deal with code uh we we do not cover any theoretical
7:45
concept concepts or strategies and question number four is
7:50
about popular technical analysis strategies um versus what we have in the
7:55
course um I won't use any of these strategies you can we you can select
8:02
them for your capstone project uh what I can say that um technical indicators are
8:08
used um as features and um indirectly
8:13
all those strategies are embedded into ML predictions so hopefully we can predict uh better than any separate
8:22
strategy um question number five does the course follow the repo um that's my
8:28
previous repo from Python invest basic fin analysis yes there are references to
8:34
the published articles and uh um almost all articles have uh the code shared on
8:42
uh on that repo um question number six um do we optimize
8:49
uh pre-tax or after tax um generally we
8:54
we do not take into consideration tax um rate here
9:00
um you can you can embed it into your strategy if you are investing in
9:06
different countries now I will answer uh some of the 2025
9:13
questions so the the course starts
9:18
today um will we learn how to analyze the impact of tariffs on the various stock
9:25
markets i would say that we we won't um the it's not economics uh lecture and
9:34
things can become very complicated i would suggest that you can include uh
9:39
specific um vertical indexes or uh other
9:45
countries um stock indexes or some factors like trade balance uh for
9:53
countries or exchange rates as proxies for um tariffs and uh the volume of
10:01
trade what's what is the timeline of the
10:08
course uh the timeline is is approximately 2 and a half to 3 months we have five lectures and two to three
10:15
weeks um distance between those lectures and when five lectures are finished uh
10:22
there is uh 3 weeks period for a capstone
10:27
project what is your best trading strategy as I said earlier I I do not
10:32
comment on the financial performance of my own strategies what I can say um is
10:39
my general approach uh that I try to define different algorithms like a
10:47
passive portfolio or fundamental strategist portfolio or options
10:52
portfolio or algorithmic trading portfolio um and I see how these
10:58
portfolios perform and I um send more money to portfolios that
11:05
perform better what are the anticipated learning
11:11
outcomes of the course what target job pros will it prepare me for and how will
11:18
it advance my professional career further i'd say that this is a practical course
11:25
for investing um we will uh discuss
11:30
later uh on the potential outcomes at different stages so I have a specific
11:35
slide on this but um I wouldn't advise this course um as a first course for uh
11:45
uh for someone who just starts the career because it it has so many different aspects and it's quite
11:54
complicated it should be different to make predictions on life flowing data and historical data will this be
12:02
examined in the course as well we use historical data or delay data 15 minutes
12:10
delayed data um what we do here is called day trading
12:16
so we do not uh use any of the live/flowing
12:22
data but you can use it for for your projects
12:28
what market will have the moon the main focus a stock market or forex market is
12:33
there any significant difference between trading in each market uh we will uh
12:40
discuss mostly stock market and mostly US market um but you can select forex
12:48
you can select crypto you can select commodities any market you want the
12:53
principles are similar would you recommend to do the ML Zoom
13:01
Zoom camp first if not how much knowledge about coding I need to have um
13:07
I'd say a ML Zoom camp or any other uh Zoom camp definitely helps and that's why I
13:14
have a specific slide on this um but it's not necessarily that you finish um
13:20
any of these Zoom cams you should have some programming language uh say if you
13:27
finish any course on Python or analytics it should be
13:33
enough is chart swap a good site since they acquired TTMR trade or is
13:39
interactive brokers better um you can trade from any broker um there are many
13:48
comparisons on on their uh user interface fees and markets that you can
13:53
access uh for our course uh it doesn't make any
14:01
difference how this addition of uh stock market analytic zoom camp is going to
14:06
differ from the previous one um it is similar uh let's say 80 to 90% of
14:14
content uh is is the same but the data is different uh we have uh the data for
14:21
the whole new year and all home assignments are new and
14:28
different what career impact can this Zoom camp have for a fresh in data analysis
14:35
i'd say uh it's it's a good project for for your portfolio but it's not the
14:41
easiest uh one so you can you can finish some other courses faster with less
14:50
complicated projects um how much information these
14:56
courses would have about nontechnical aspects um not not much
15:04
i I try to uh add context um to the home assignments and to to the slides so that
15:12
you can click and read uh the the articles u uh but uh not more than
15:21
that does simple analysis like using technical indicators for buy signal generate more wins than put more effort
15:29
on building accurate model we will discuss this um we will use uh hand
15:35
rules and uh specific technical indicators first and then try to to compare uh with
15:43
um uh ML predictions that have those technical indicators as
15:49
features okay last question and and then we continue with slides can you give an
15:56
example of streaml um there there were two um webinars in February this year
16:03
and December last year and those uh webinars are linked uh at the GitHub um
16:09
course page so you can check them and check uh the repos from from the
16:16
webinars i believe uh that dashboards are still alive and you can check them
16:22
as well they they were built with streamlit okay now let's uh move on uh
16:29
with the content questionnaire um I've updated
16:38
stats uh with the data from today um one month ago it was about 400 submissions
16:46
and now it's more than 1,000 um we have uh 68 countries with more
16:54
than one participants top 10 countries um are USA India Germany UK Nigeria
17:02
Canada Colombia France Spain and Singapore and they are 62% of all
17:07
respondents um then 355 of you approximately
17:16
35% answered that they um took uh some
17:21
of the previous um Zoom camps by data talks and as you can see um data
17:30
engineering zoom camp is is the most popular one i'd say that any of these
17:35
zoom cams uh will help you um and um analytics in stock market zoom
17:44
camp uh that's um we had last year will help you more than others because the
17:52
content is quite similar um then I I checked all of your answers
18:01
on the um knowledge application and uh I
18:06
colorcoded them uh whether they are the best fit medium feed or low fit uh so
18:13
first uh we will be analyzing and predicting stock market trends we will
18:20
um develop trading strategies and algorithms to automate trading we will
18:26
create person personal investment portfolios based on on these uh
18:32
strategies um medium feed is cryptocurrency market and crypto trading
18:40
because um you may need to have more granular data you may need to add
18:48
additional features uh I'm not focusing on this but you can definitely apply uh
18:54
these um approaches on crypto then we are not focusing on uh building
19:00
financial dashboards and tools um just if you have any automation it
19:08
should be enough if you have a dashboard it it's very good
19:13
um we will try to understand the financial markets uh for for personal
19:18
and interest so we will discuss uh economics we will discuss uh different
19:24
uh data trends um you can see um other uh
19:30
applications here and these applications can help you to choose um your own
19:38
project um I also added um other application se uh section uh
19:46
just to highlight that say many people don't have any idea yet um that's why we
19:53
have a specific question on uh in in home assignment one to uh brainstorm on
20:00
on the idea and you can see a huge variety of of ideas uh and applications
20:07
here hopefully all of them will be
20:15
implemented now we talk about course objectives versus expected outcomes i
20:22
treat them as a seven levels of complexity so if you start from from
20:28
from the level one the easiest level you get uh some skills you can replicate
20:35
notebooks uh you can run code so it's Python analytics and finance skills uh
20:42
then you might want to start trading uh and you can get additional skills uh
20:49
when uh and knowledge when you register with the broker you transfer some funds and you practice small tra trades you
20:56
understand that it it's not that complicated you can see how to operate
21:02
with uh this new industry then level number three it's it's a
21:08
leaderboard i know that some of you are quite competitive and we have a leaderboard which is updated every every
21:16
week uh on the data talks um course management platform and it is
21:22
transparent so you have this link uh to the leaderboard in the home assignments you can check it every day so some of
21:31
you want to compete and to complete all homework assignments and all open-ended
21:36
questions that's that's great then uh you might want to build a
21:42
portfolio so that you you create your own project um that generates trade
21:49
recommendations that utilizes your local knowledge and your own passion and you
21:56
share it on GitHub or in social networks so that um it's it's uh
22:04
uh your own thing uh next level is that you you start to
22:10
do the investing decisions with uh um with the code from from that project so
22:17
you customize the the code for your market your product or idea you experiment with the models hopefully um
22:25
you can reach profits like consistent profits not one day profits but every
22:31
months every 3 months you you can have um some returns on uh paper or real
22:39
money trading and uh the most complicated uh objective is a long-term
22:47
um sustained profitability um that you can not only develop one
22:55
um one model um but you constantly look after this model or other models um you
23:03
track your trades you understand your mistakes you add more features and uh
23:09
you start using this knowledge uh from today to the uh next uh few years
23:19
um now let's talk about understanding datadriven
23:26
decisions so here um we start from some
23:31
microeconomics indicators and we will check uh how
23:36
these indicators can be obtained uh with uh Python code just uh with a few lines
23:43
of code so um you can you can open um the the
23:50
code so if you type collabress research.google.com and select GitHub
23:57
and select the um address from uh from
24:03
the notebook so you should be able
24:08
uh you should be able to find this and and open uh this um notebook and then
24:17
you can connect uh a new runtime and you can run all um and follow what what I
24:26
show you here so I have this this notebook uh opened with the saved runs
24:34
and for for the um data section um we have a few imports before just a
24:43
few libraries the most important library is Y finance where we get uh daily data
24:49
for most of the financial assets and say
24:55
for for GDP uh we uh get the data um with this line
25:02
of code uh we call appendas data reader um we call
25:09
the metric GTP port uh this metric is from uh data database Fred
25:16
um and it returns a data frame like this dates and GDP port um column i define
25:25
two more columns um growth year on year and growth
25:30
quarter on quarter and you may want to read uh what does it mean when you shift
25:36
uh the data on one or four um data
25:42
points so the uh the logics is exactly the same for most of the data STS that
25:49
we have here we just select different metrics from a different source um we
25:55
get the the data frame and then we might build some visualization um so that's what you see
26:02
on the slide let's um return to this to the slide so real
26:09
potential GDP this is uh this is a US uh
26:14
GDP um this is the the first uh macro indicator that is used in in many
26:23
um economic studies uh you can uh see
26:28
here that the the prediction is is stable it's um about two to 2.5 um
26:36
percent growth every year and we observe some acceleration of growth after COVID
26:43
year but uh overall the the growth is uh
26:48
the growth rate is is very different now versus uh you see it 10 years ago or 20
26:56
years ago
27:01
um then next thing is um inflation most of you know that um all
27:09
prices are constantly growing and if you do nothing you
27:14
uh you're just losing um money because you can buy less uh foods or less things
27:22
on on money that you have so that's why we track inflation um and there is a
27:29
specific um matrix on FRA you you can see this this links so you can download
27:36
this matrix in the exactly same way that I showed you previously you just substitute the the metric name and you
27:42
get the data for that metric and uh uh recently in the US and many other
27:48
countries uh inflation was quite high after COVID and uh many central banks
27:55
were fighting against inflation and uh many of them are successful so inflation
28:02
went down um in the last uh two three years and
28:08
it's still going down so um core CPI declined from 3.7%
28:16
uh last year uh in February 2024 to 2.8%
28:22
in March 20 2025 now you know that uh you need to
28:28
save money uh with the rate uh higher than 2.8% just uh to have uh the same
28:37
buying power um now let's uh think a little bit
28:43
about your personal uh saving options uh
28:48
let's assume that um you have um income in dollars or euro um you know your
28:59
inflation rate in in Ireland it's 2.2% in the US it's
29:04
2.8% and uh you you think what you can do with your money so first thing do
29:10
nothing it's not bad so you are not losing anything it's 0% interest it's
29:17
full liquidity you you can use your money any day next thing um you can go
29:25
to a bank and open a saving account uh for example in Ireland is two to 3% in
29:32
in euro um you might um get a rate which is
29:40
close to to inflation but in many countries it is lower than inflation um
29:46
you have money protection scheme so that bank guarantees to return your money uh
29:52
or some uh amount of money um up to some
29:58
threshold so um it's still low risk but returns are not very high and next uh
30:06
thing um there are money service businesses um like Wise um that uh offer you
30:16
slightly higher um returns on your money and you you can also uh transfer funds
30:24
to to other countries or do easier payments with these services so strictly
30:29
speaking they may not be a registered bank in your country um it can be some
30:35
global organization and they can offer you a slightly high returns but it's
30:41
it's a marginally high returns not not u high enough and
30:48
uh strategy number four you open a broker account uh and try to invest um
30:56
money there in some um broker accounts like Interactive Brokers or Trade
31:03
Republic um you can get um a decent uh return on
31:10
on your uninvested money like uh up to 4% in in dollars uh in Interactive
31:18
Brokers it's down from 4.8 4.8% last year and up to 3.25
31:27
25% interest uh on euroash in trade republic but there there can be some
31:34
additional conditions that it uh your money uh do not have a protection scheme
31:41
um or you need to have minimum 10,000 on your account etc
31:48
etc when you already have uh some of your money uh on broker accounts you are
31:55
thinking what can I do better how can I invest those money
32:01
and uh um let's assume that uh you're in in the US and uh you you think what's uh
32:09
what's the benchmark what should we see as a minimum returns of on the
32:17
investments and um um in in the US um the most important
32:24
rate is a fat funds rate so you can read more about this trade uh on Fred the uh
32:32
or other um links here uh
32:37
the important thing is that um it's slightly higher than 4% so it used to be
32:45
5.3% last year and now it is 4.8% I think 4.3%
32:53
there there were uh two uh rate cuts um
32:58
or three rate cuts in 2024 and there are two expected rate cuts in 2025 so if you
33:07
see um this uh you can expect that uh stock markets and other markets uh will
33:15
uh change their returns um especially in in the US because all these markets are
33:23
connected um there is a derived metric uh which is
33:28
uh called risk-free rate and typically it's a three months T bill which is
33:34
close to 4.3% uh it is 4.2% 2% now um and
33:42
uh this this rate is is used for um for
33:47
discounting for um future uh uh payments that you might
33:54
get and you need to discount it to the current payments for for economic models
33:59
but for you uh you can you can see that um
34:07
um you want to to get um something which is higher than risk free rate which is a
34:15
4.2% and first thing uh is a is a bonds uh
34:20
it's not stocks it's it's a depth instruments say if you buy corporate
34:26
debt or government debt and uh essentially it's a loan and they say
34:33
that uh they they can pay you um five six 7%
34:39
uh it is a some rate which is higher than risk-free rate but it has some
34:45
additional premium for for the risk say risk of default
34:52
uh so if you choose this and it is um used very often in passive portfolios um
35:00
you you can get um regular dividends or returns uh payments from from bonds um
35:08
and these payments can be uh five six 7% in the US uh with a small risk now uh if
35:18
you start investing in stocks and uh if if you're in the US um first um you want
35:27
to look at some broad market index uh S&P 500 for example um and this index um
35:36
it's um it returned on average uh 10%
35:43
uh during the last 35 Yes but some years like this year now situation is slightly
35:51
better but um uh as of mid midappril or end April it was minus 6% so you could
36:00
uh have not plus 10% or plus 5% but you could be minus 6% just in in three
36:07
months in uh in four months of this year so uh the idea that I try to deliver
36:15
here that if you expect uh higher returns you should also expect uh more
36:22
risk or more volatility of of
36:27
returns and this is a concept uh rule of 75 72 so how quickly can can you double
36:36
your real capital and approximately if if you say that I want to achieve uh the
36:45
uh rate of return of 10% uh then you can double your capital in
36:50
seven years if you uh stay with with the local bank probably you double your
36:58
capital in somewhere between 23 and 35 years
37:06
and if you are doing really well and some some years uh like previous two
37:12
years for the US um stock markets delivered more than 20% then um you can
37:18
get um you can double your money in in four
37:27
years if we combine everything that that's um I talked uh
37:34
previously so uh what should you look at um when you
37:40
define your your strategy first we want to have a positive return and ideally
37:47
positive return should be every every months or every six
37:54
months or every roll in period so it it may be not every week but if you select
38:01
randomly six to 12 nums uh months you should see a positive return um then uh
38:09
60 to 40 portfolio that's a famous uh passive investment portfolio which
38:15
combines equity which is stocks 60% of uh stocks and 40% of uh bonds and uh um
38:25
this portfolio um for risk averse investors and it's um
38:32
delivered approximately 7% of uh returns or about
38:38
5% inflation adjusted s&p 500 um index in in the US
38:45
had 10.5% returns or 6.3% inflation adjusted and now um it it comes a sweet
38:54
spot um that's how I define a a good rate of return for myself um so um if I
39:04
have um six to 10% per year net of inflation every single year I treat this
39:12
year as a successful year and uh it's not 50% it's not 30% just you you can
39:21
compare yourself versus u most famous hedge funds and investors like Warren
39:27
Buffett who delivered uh 20% of average um growth uh average annual uh growth
39:35
rate over several decades so if you believe that you can be better than
39:40
Warren probably you can try to define a higher rate of return for your portfolio
39:47
and you can also check some of the largest uh hedge funds like Renance
39:52
Technologies uh they said that they achieved 66%
39:59
uh average uh annual growth rate which is incredibly high
40:07
um and uh um continuing previous slide there can be different asset classes
40:15
like um stocks of US stocks or uh emerging
40:21
market stocks or commodities or uh like gold or bonds and um all these classes
40:30
they have some expected annualized return so you can see it can be 4% or it
40:37
can be 12% and these classes they have annualized
40:43
volatility it's um deviation of a return or risk that um you can get uh when you
40:51
buy this class so it can be 0% or it can be 22%
40:56
and if you combine um few classes or all of these classes
41:03
there is a theoretical efficient frontier which is a theoretical concept
41:08
but it's good to understand that if you select a few um investment classes you
41:16
can get um nearly optimal theoretical uh
41:21
returns um from from those classes and you can calculate th those returns using
41:29
historical correlations uh now let's uh think about
41:36
more practical things what you need to do when you think about your project and
41:41
when you are thinking about yourself so first uh you need to decide uh about
41:48
your risk toler tolerance um what's your expected return uh what's
41:55
your um maximum draw down um what are
42:00
you going to do in the next few years and uh as a general guidance it is often recommended to take more risk earlier
42:07
when you don't have a lot of capital and uh you can um make mistakes but you can
42:15
also learn uh on how to invest in different asset classes but when you do it for 10 or 20 years and you have some
42:23
capital you're selecting um more risk averse strategy
42:29
uh then you try to define success uh whether you select some benchmark
42:36
uh like um S&P 500 index or you can define
42:43
specific metrics um like sharp ratio ratio or maximum
42:49
drawdown that's uh define your your success and constraints
42:57
for for the portfolio selection from a data perspective um it's um important to
43:04
understand that all markets are interconnected and uh we are building
43:11
some form of a model of a world so we
43:16
are using data a little bit of data from
43:21
um all major investment uh classes um or
43:28
markets and then we add more data on a specific uh vertical or specific
43:34
um country um trying to predict that um
43:40
small market but understanding that that small market is uh connected with the
43:47
major uh large markets and now let's have
43:57
um pra let's talk about collab i saw um questions uh on on
44:05
collab why I'm using it and whether I um
44:11
ask everyone to use it um of course uh you can use whatever you want um I use
44:19
collab because of a few things that it's uh low barriers to start so uh you do
44:28
not depend on your environment it runs in your browser and in many cases it's
44:33
enough for our um goals then you have um
44:38
that you already have a lot of pre-installed libraries you have uh free GPU GPU
44:45
access that's uh useful when you're training models that have millions of
44:51
um records um with um say 200 features that we can generate um uh during this
44:59
course um so it can increase the speed
45:05
uh of your um model training um it's easy to share with with
45:12
everyone it's easy to save and you can see the output you can also have dynamic
45:17
visualizations after um the output is produced there are some graphs um that
45:24
are rendered on on a website and you can select uh countries say on on the
45:31
country split and or you can select specific date and you can see a a value
45:37
that is shown on that graph so that's uh very convenient it's cloud-based so
45:45
any device anywhere autosaves your work there are some uh uh pros as well uh
45:52
sessions may disconnect and they will definitely disconnect uh if if you wait say more than one hour you may need to
46:00
re-upload files if you're using some local files but you can also use your your drive and you don't need to upload
46:07
files or you can use a database uh then there are free tier usage limits so uh
46:15
there are paid plans for collab in in most cases free tier usage limits is
46:21
enough what else do I use um I uh normally develop in Jupiter notebooks
46:28
and aonda um with a full local control and I normally um have an IDE like VS
46:38
code i showed um this uh setup uh at the
46:44
previous uh workshops in December and February and it's ex extremely
46:50
convenient and useful because it has a powerful AI assisted development you
46:57
need to pay some money for this but it's as of today it's much more powerful than
47:04
AI in uh collab um so what what are the data
47:12
sources uh for for the stocks uh you might want to use i I'll um talk about
47:19
them now and I will show them uh in in a callup first uh it's Yahoo Finance it's
47:26
a free data source and it's open high low close volume data we use daily data
47:33
but you can have um hourly or uh minute data with uh lower
47:41
um minimum and maximum start date say if you if you use u hourly data you might
47:48
have only two years of history uh from Yahoo Finance but if you select
47:54
polygon.io IO or Alpha Vantage or any other uh paid provider uh you can you
48:01
can get all of this data um for um more
48:07
years then uh we will generate technical indicators um from from that data uh
48:16
this uh this is covered in model two um and we will use a library called
48:24
TA-LIP um and it will produce approximately 100
48:30
technical indicators so if you are a technical uh trader you will see um very familiar
48:39
features in in a data set that we will build um then you saw some examples of a
48:46
macroeconomic data um I'm using
48:52
usually somewhere between 50 and 60 uh features uh from from this um data set
49:01
FRED um if you are um investing in Europe you might want to use some other
49:08
database on macroeconomic data like Euroat um it's slightly harder um because u
49:17
their API is not that convenient but it's possible to use um then if you are
49:23
doing a model on u financial uh on on stocks you might
49:31
want to use financial reporting stats in some way and that can be earnings per
49:38
share profitability revenue and um um
49:43
financial metrics that companies provide every quarter and every year to the
49:49
regulator uh I saw many of you want to analyze news um I wrote a few articles
49:57
about it um on pythonbest.com it's quite challenging to
50:05
um analyze news because uh normally um free or um
50:13
uh paid providers they they do show you news only from a short period of time
50:19
and if uh you want to uh train your model on 25 years of data um it's uh it
50:28
can be hard to uh generate
50:33
features for uh from the news uh of 25 years of data
50:39
um okay fundamental data here it's a synonym for financial reporting uh so
50:47
Yahoo Finance a free um provider will
50:52
give you some snapshot of a fundamental data uh of financial reporting for the
50:58
last uh one to four years uh if you use paid providers you you can get 25 years
51:06
data easily you can also do web scraping which is uh harder uh but sometimes you
51:13
have to do this because it's it can be um too expensive to get data uh from
51:22
paid providers then um if you are building something uh some model
51:29
um in a specific vertical you might want to use alternative data uh it it can be
51:37
anything uh social media sentiment uh app usage credit card data glass door
51:44
reviews YouTube uh videos or commentaries web traffic on
51:51
websites um satellite imagery anything uh that is connected to the companies or
51:58
stocks uh that that you want to invest in and you want to build a model events
52:05
events um are um also quite powerful
52:13
um indicators and we want to consider uh we we want to understand what are the
52:21
most important events like earning calendars when companies do the
52:26
reporting um ETF flows it's
52:32
u um exchange exchange traded funds flows of money it's it's another form
52:39
that uh funds um provides uh to to the
52:44
financial reporting um
52:50
um and they they um
52:57
um they have specific uh dates uh when these flows
53:02
change uh so um before
53:08
you try to uh combine that many data
53:13
sources I I'd advise you to play with the data and um a popular
53:22
um tool is called stock screener um you can find many stock screeners by um
53:30
different providers and many of them are free um say this
53:37
one is from Trading View i like their graphs i I like their um um their description of matrix and
53:47
what are the values for the matrix that you might want to uh to find say if I uh
53:54
want to look at the US market uh only companies in S&P 500 that uh pay some uh
54:02
dividends more than 2% that are growing on revenue
54:08
um more than 0% year on year uh that are not too expensive um this metric PEG
54:17
less than 0.5 and that have upcoming earnings next week you can get this with
54:24
just a few clicks and then you get some uh understanding uh on on the data so I
54:32
highly recommend to play with the with this um stock
54:38
screeners okay let's look at the main data source daily um data
54:47
so if you scroll down uh here all so data data sources for
54:55
stocks indexes you will have um um home assignments
55:02
um that is already published and uh that home assignment uses uh this uh data
55:10
provider I think in in every question so
55:15
um you can just um reuse this code
55:21
um so there are
55:27
um uh there there are a few examples uh you need to import Yahoo Finance uh library when
55:36
you imported this library you select a ticker and this is um um index ticker
55:43
for um uh for a German stocks market DAX daily
55:52
when you import when you download data from for this sticker you can specify
55:59
start and end dates and you get data like this open high low close volume uh
56:07
and you can generate um additional columns uh based on this data say
56:16
um growth um year-over-year
56:23
um uh it's it's about 20 252 trading days uh in a year you can divide close
56:33
um um value for this day on a close uh value for uh one year ago and uh you
56:42
will have a growth um of this index um
56:47
year-over-year um
56:52
okay I also suggest you to read uh some of the examples um Y finance the
57:00
definitive guide or Yale lectures
57:06
um just to to check uh the the code there and the description on the
57:13
available options um we won't focus um today on
57:21
the pay data um I think if if you if you're using um if you want to to
57:29
have some news data you have to use some uh paid data providers or free tier on
57:37
those pay data providers so I added links uh on my articles um on the
57:45
financial news summarization that uh is using polygon.io your news
57:53
API alpha Vantage also offers 25 free calls and my last article on the
58:00
fundamental data uses Alpha Vantage so you might find um some good data there
58:08
as well microeconomic stats
58:13
um in most cases uh we will use uh stats
58:19
uh from FRET Federal Reserve Economic Data um if you open that website it
58:27
there are uh thousands of of data points and you may not know which data points
58:34
to choose that's why I um suggest that you try to check on other uh sites um
58:43
what are the mostly used macro u
58:49
indicators like uh this US indicators and um you can then search for those
58:56
indicators on Fred and uh find uh those data points otherwise it's it's quite uh
59:03
hard to compile a good um subset of metrics on on macro
59:11
from Fred financial reporting i provide some
59:16
links here that uh you can download um data uh from
59:23
uh from from the stock exchange uh for free but usually they are not very um
59:31
structured they are not um compiled into one data frame so if you can um write
59:39
code for this um you can download um this precious uh data for
59:47
free web scraping i had a few articles on this and the idea is that there are
59:54
numerous financial websites and they can provide um a good
1:00:01
um data that you want to use um on the web uh web browser UI and
1:00:10
sometimes uh these uh websites can even uh pro can even
1:00:18
uh give you an opportunity to download this data uh if you open this coin uh
1:00:24
company's market cap uh page let's open it now you can see this this uh button
1:00:31
download the list so you can uh in this case you you can quickly get data from
1:00:38
from this uh website but many others um they they are
1:00:44
not um I won't use it this um during this course but uh please uh take take a
1:00:52
look at um things like Google trends or um
1:00:58
Twitter uh sentiments they can be quite powerful as
1:01:04
Well recap for today uh what we learned uh
1:01:10
today first uh we discussed um concept of a financial rate of return
1:01:18
and efficient frontier and uh uh the balance between risk and reward
1:01:24
then um we
1:01:30
um we were chatting about how you going to develop your investment idea what are
1:01:36
the features for for the capstone project that you might want
1:01:41
to to get we looked at some of the macroeconomic data and indicators
1:01:48
um we checked uh stock data sets and uh
1:01:54
now we will cover a cheat sheet for starting a project um if uh you u simplify all of
1:02:04
these um materials here is a stepby-step guide um what you need to do for your
1:02:11
project first you select one market or country you can go global as well but
1:02:18
it's harder to get a a good data set for for this then you choose uh one or a few
1:02:25
benchmark to compare with it can be an index or some per good performing asset
1:02:33
class or it can be even a banking rate of return then you select macroeconomic
1:02:38
indicators or some other indicators that might affect uh your specific market
1:02:46
um next step you think about the data set size how many companies do you want
1:02:52
to include what a time period and history do you need in um in this course
1:02:58
I normally use 25 years of data and I ask uh to uh have more than 1 million of
1:03:08
uh rows in your data set so that um um our ML model with u hundreds of features
1:03:16
can can be trained in some way and produce u good results then um you need
1:03:24
to decide do you need the fundamental data normally it's hard to get this data can you provide only four years of data
1:03:32
do you need to scrape this data etc and last step um do you want to include any
1:03:39
alternative data important note is uh not to leak the data um at any
1:03:48
um point at any date you you need to include
1:03:54
um the the data that is already available at this date so you can't
1:03:59
include um something that will be reported at the end of the year or at
1:04:06
the end of the quarter if you have a historical data because it will it will bias this the estimation and you you
1:04:13
won't get uh the the correct predictions and uh um last uh lastly
1:04:23
some generic recommendations for the course be active ask questions and
1:04:29
contribute to discussions you have Telegram you have uh Slack if you have
1:04:34
any problems I regularly check um those channels you can ask questions and
1:04:39
hopefully you can help each other prefer the simplest option when possible and build on it so you can reuse class
1:04:47
materials you can start from one stock you can start from 10 features do not try to build the
1:04:56
um the best picture of the world just from the attempt number one then home
1:05:02
assignments they are important they are designed to be straightforward they are not always simple because I want you to
1:05:11
get some intuition in the recent economic um advancements and and data
1:05:18
and sometimes um the technical aspects uh uh can can
1:05:26
be quite quite hard because you need to spend some time uh when you download the
1:05:31
data when you uh work with the data and get um uh some result so I don't expect
1:05:38
you to to solve all home assignments but please try to solve one problem two
1:05:45
problems like something do something every single uh lecture and you will see
1:05:51
that there are different point assignments close to the assign to to the questions uh next um start working
1:06:00
on the project early uh and it's not uh only about projects it's it's also about
1:06:06
home assignments every single week and and uh every single time I see people
1:06:13
who are asking to extend the deadline so my best advice to you is to start
1:06:18
working on on the assignments today and last but not least leverage uh your edge
1:06:25
so if um if you are just starting out
1:06:31
um build new skills uh and build a portfolio uh that uh will uh will be
1:06:39
helpful for your uh next job position then uh if you're already investing in
1:06:46
some local market consider choosing that specific market if you're a advanced uh
1:06:52
software engineer you you can build a simpler model or simpler um data set but
1:07:00
more complicated automated solution um as as a project same same advice is for
1:07:08
ML practitioner or a trader um and if you are a student then you have the most
1:07:16
precious resource time so I I saw some examples when people had zero experience
1:07:23
but they spent three five times more um than than others on average um and um
1:07:32
they they succeeded so they they finished uh with the capstone project
1:07:39
homework so homework um actually I think it it has four questions and two extra
1:07:46
it's already published in uh 2025 cohort homework um
1:07:53
1.MD the deadline is to submit within next two weeks so end of Monday
1:08:02
um GMT + one um time
1:08:07
you can get extra points by posting your your um homework um and tagging Python
1:08:15
best and data talks club uh this year we reduced these um uh points from seven to
1:08:22
three uh first of all we we want everyone to solve the questions and not
1:08:27
just uh post those questions on the social media and we can um check and the the
1:08:37
homework so it's it's here
1:08:42
um there are questions S&P 500 um there are links um
1:08:49
you can see the context just for you to understand what to expect why I ask uh
1:08:56
these these questions and uh what should be the the answer uh so four questions
1:09:04
question number two number three and number four sometimes I make your life
1:09:11
easier um so I do not provide uh I don't ask you to download um data uh from
1:09:18
Yahoo Finance to scrape the data uh I scraped it already and I added it to uh
1:09:25
to the folder so you just uh download uh the CSV and work with with the data
1:09:30
frame or sometimes I provide the uh part of an answer in in question number three
1:09:36
I ask uh to uh to get the median duration of
1:09:44
significant market corrections and I show you examples of top 10 um market
1:09:51
corrections so if you solve this question you can just check what you have and if it's approximately correct
1:09:58
then you you can uh get your final answer and uh then five questions number
1:10:05
five and number six they are exploratory um to think about your capstone project
1:10:10
and to investigate on the new metrics you have a form for
1:10:15
submitting you can see that it's it's already open due date is 2nd of June and
1:10:22
it will be your local time here are numeric answers and
1:10:28
um um you need to provide homework URL please provide uh real URL for a GitHub
1:10:37
or G or any other uh URL that um shows
1:10:43
your code okay
1:10:49
i think that's that's it for today folks um see you in probably two to three
1:10:56
weeks i will announce uh on the next date uh on Telegram and Slack and I will
1:11:03
plan uh the live stream on YouTube as well thank you guys and happy learning