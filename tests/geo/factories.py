from random import sample

import factory

from itou.geo.enums import ZRRStatus
from itou.geo.models import QPV, ZRR
from itou.geo.utils import multipolygon_to_geometry


ZRRS = [
    # In ZRR:
    ("12018", ZRRStatus.IN_ZRR),
    ("28271", ZRRStatus.IN_ZRR),
    # Not in ZRR:
    ("85204", ZRRStatus.NOT_IN_ZRR),
    ("62626", ZRRStatus.NOT_IN_ZRR),
    # Partially in ZRR:
    ("86281", ZRRStatus.PARTIALLY_IN_ZRR),
    ("97405", ZRRStatus.PARTIALLY_IN_ZRR),
]


def _params_for_zrr_status(status: ZRRStatus) -> dict:
    [(insee_code, status)] = sample([elt for elt in ZRRS if elt[1] == status.value], 1)
    return {"insee_code": insee_code, "status": status}


class ZRRFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ZRR

    class Params:
        in_zrr = factory.Trait(**_params_for_zrr_status(ZRRStatus.IN_ZRR))
        not_in_zrr = factory.Trait(**_params_for_zrr_status(ZRRStatus.NOT_IN_ZRR))
        partially_in_zrr = factory.Trait(**_params_for_zrr_status(ZRRStatus.PARTIALLY_IN_ZRR))

    insee_code = status = None

    @classmethod
    def _adjust_kwargs(cls, **kwargs):
        if insee_code := kwargs["insee_code"]:
            [zrr] = filter(lambda zrr: zrr[0] == insee_code, ZRRS)
            return {"insee_code": zrr[0], "status": zrr[1]}
        # If no params, return a random commune in ZRR
        return _params_for_zrr_status(ZRRStatus.IN_ZRR)


QPVS = [
    (
        "QP075019",
        "Les Portes Du Vingtième",
        "Paris 20ème arrondissement",
        "SRID=4326;MULTIPOLYGON ((("
        "2.4128913231573907 48.874084057785005, "
        "2.4130577969483578 48.87408361150439, "
        "2.413368910541289 48.873091383792826, "
        "2.412331979439107 48.87231286779905, "
        "2.4121549991403985 48.87221553991153, "
        "2.410936916152377 48.87125431370065, "
        "2.410738911248298 48.87065160352192, "
        "2.4108746519460262 48.869178572596134, "
        "2.4109401038626994 48.86844518223567, "
        "2.410987819358849 48.868016498308, "
        "2.4109943995165053 48.867856279677824, "
        "2.411058934024765 48.86720301483475, "
        "2.4111429931162336 48.86650899232041, "
        "2.411514299979107 48.86568284108942, "
        "2.411732099191621 48.86543282366727, "
        "2.4116790062520863 48.86494500949258, "
        "2.4121538780089633 48.86471817866581, "
        "2.412796222789813 48.8643505487554, "
        "2.413011015149648 48.86388655028963, "
        "2.4130926593768622 48.863135487259065, "
        "2.413241303658235 48.86197010912357, "
        "2.413400677979484 48.86152465872703, "
        "2.413495674017409 48.86106508935682, "
        "2.4132193309021384 48.86110216000133, "
        "2.4130570521170758 48.86111358626585, "
        "2.412871331192997 48.86110134892967, "
        "2.4128723438719115 48.86110074954008, "
        "2.4128181436440475 48.861560340530005, "
        "2.412740994017292 48.86249006801689, "
        "2.410960695144741 48.86241218998951, "
        "2.411053094707801 48.86182190151859, "
        "2.411203179550702 48.8607310401518, "
        "2.4113900447226553 48.859818806176946, "
        "2.4115695889514135 48.85870122573064, "
        "2.4114913904323165 48.85717736369243, "
        "2.414626734897289 48.85826984068669, "
        "2.4152528503235846 48.85428640038002, "
        "2.4155772196515355 48.85270604087029, "
        "2.415757719690726 48.851689181158854, "
        "2.4154676459934024 48.85075204299812, "
        "2.413257710687523 48.850937174783404, "
        "2.412825922860528 48.8509861036952, "
        "2.4126922409160465 48.851002947137516, "
        "2.411790728589733 48.85132409236792, "
        "2.4109056391390236 48.85127574888895, "
        "2.410956170151918 48.85101832839971, "
        "2.4112736574162863 48.84904653996858, "
        "2.4101691728114134 48.84903481362177, "
        "2.410138964844086 48.849488844616616, "
        "2.4099646738317935 48.85035849623086, "
        "2.4096965040129037 48.851016334657345, "
        "2.4094712461767496 48.851472963673345, "
        "2.4098709469253565 48.851520128061686, "
        "2.410135173350746 48.851778447211125, "
        "2.410367203082847 48.85194851574197, "
        "2.4109640599434594 48.85200504417396, "
        "2.4109366344760588 48.85274648384904, "
        "2.4107849089336235 48.85353130532919, "
        "2.410587690166149 48.854127362710635, "
        "2.4104953153289217 48.85471765499564, "
        "2.4101233401113182 48.85476609717217, "
        "2.409508283124453 48.855256476075596, "
        "2.4097084051960027 48.855516480804035, "
        "2.408433446936006 48.85569364591241, "
        "2.408044975767244 48.85579906903045, "
        "2.406767524902673 48.855974979165026, "
        "2.405872103810416 48.85609465731069, "
        "2.4057804604575836 48.85624080296787, "
        "2.405896155057125 48.85632260462067, "
        "2.406879502288287 48.8571527857591, "
        "2.407576229349176 48.85772733051103, "
        "2.4084353014473625 48.85721354666167, "
        "2.4092956729328563 48.85669977909363, "
        "2.410001509586943 48.856273782185745, "
        "2.410230421475138 48.8562434892714, "
        "2.40995685589217 48.85769386809648, "
        "2.409914780665611 48.858045592304805, "
        "2.4099118544080196 48.858303245539005, "
        "2.4096816293261094 48.85928877523911, "
        "2.4093558540266202 48.86114109708453, "
        "2.4092114696723717 48.86211447969816, "
        "2.409058265224176 48.86302497541661, "
        "2.4088364611196402 48.864104809880736, "
        "2.4088481992683453 48.86432953736446, "
        "2.408891882212437 48.86509645985165, "
        "2.408972930661755 48.866349047155445, "
        "2.4091357314592847 48.86795238410443, "
        "2.4090743798324237 48.86832286335929, "
        "2.40903660602359 48.869133374525084, "
        "2.4089620790467388 48.86982429526631, "
        "2.4089533799905727 48.87059095522562, "
        "2.4103246209949307 48.870641706676544, "
        "2.410515354516603 48.870623792511815, "
        "2.410718312585108 48.871209249467476, "
        "2.410619500342871 48.871522983057226, "
        "2.410605278247086 48.87193768751517, "
        "2.4105235939476195 48.87242118235617, "
        "2.4102433457399193 48.87339293750155, "
        "2.411452124268841 48.87371563163225, "
        "2.4128913231573907 48.874084057785005)))",
    ),
    (
        "QP094025",
        "L'Egalité",
        "Champigny-sur-Marne",
        "SRID=4326;MULTIPOLYGON ((("
        "2.5203776956356165 48.818104418744454, "
        "2.520393823742997 48.818804744092176, "
        "2.521392512354362 48.81877399410346, "
        "2.5214731207938996 48.81876905542298, "
        "2.521460811022171 48.817128417695315, "
        "2.52117770532817 48.81709501494015, "
        "2.5206349808800055 48.81703158247557, "
        "2.5200852255439896 48.81696602019054, "
        "2.51995748044359 48.816944262481954, "
        "2.5198240607975513 48.81699923223445, "
        "2.519814866540772 48.81705797089698, "
        "2.519813145608504 48.817098441001285, "
        "2.519828568660828 48.81719651979915, "
        "2.5201064741585313 48.81813500626882, "
        "2.5203776956356165 48.818104418744454)))",
    ),
    (
        "QP093028",
        "Franc Moisin - Cosmonautes - Cristino Garcia - Landy",
        "Aubervilliers, La Courneuve, Saint-Denis",
        "SRID=4326;MULTIPOLYGON ((("
        "2.417826743976493 48.92398268473545, "
        "2.4177062013397443 48.92377974792261, "
        "2.4172955795400335 48.92321503508745, "
        "2.4168992956946775 48.922653956872466, "
        "2.416716562624647 48.92237961093957, "
        "2.4165090516027536 48.922104847223736, "
        "2.4164542146421604 48.92200655556154, "
        "2.4162900327067725 48.9218007118851, "
        "2.4162596994669587 48.92176983530011, "
        "2.415970238084385 48.921477205138004, "
        "2.4156847887310957 48.92118996252429, "
        "2.415432043733089 48.92094792787918, "
        "2.4152612899402435 48.920810981301315, "
        "2.4149195861532626 48.92049724950054, "
        "2.413559123621677 48.91940514359232, "
        "2.4134631298757405 48.91944695492102, "
        "2.413227016671808 48.91957079711696, "
        "2.4129619801529936 48.91971967916348, "
        "2.412896009155334 48.91976073063702, "
        "2.412795051627042 48.919807707824475, "
        "2.4127773269497093 48.91979599308382, "
        "2.4123401868974863 48.920009399792576, "
        "2.4121665627421884 48.920071004047045, "
        "2.4120470761925366 48.92013966698794, "
        "2.411856627770374 48.92020617391392, "
        "2.4113584408281405 48.92045733362484, "
        "2.4109262433434235 48.92066563341021, "
        "2.4105659780186524 48.920829203927084, "
        "2.4103704689341883 48.92066921271759, "
        "2.4091940807547623 48.91962650841482, "
        "2.4094462327260335 48.91953243529463, "
        "2.4101455718712175 48.9189891162722, "
        "2.410597325081318 48.9186226141189, "
        "2.4112099140748837 48.9181472100128, "
        "2.409790411127438 48.916977430393956, "
        "2.409699603712069 48.916923025216136, "
        "2.409268989108067 48.91723476986485, "
        "2.409092790268359 48.91737147712419, "
        "2.40898154757817 48.91742667759112, "
        "2.4084631736449182 48.91767512549502, "
        "2.4076210180189412 48.91804138459353, "
        "2.4060848238696724 48.9166164752395, "
        "2.4057097413368735 48.916332253876924, "
        "2.4051195161026624 48.915800542963446, "
        "2.404327041422228 48.91506277792252, "
        "2.403579036312238 48.9143719829952, "
        "2.403190337027452 48.91400133627071, "
        "2.403048712225828 48.91385763660667, "
        "2.4027780159831407 48.91354873767167, "
        "2.4014900724545707 48.91235522786258, "
        "2.4005410881200104 48.91147275198765, "
        "2.4004033719596976 48.91134557953687, "
        "2.3999267044194807 48.91091356727912, "
        "2.3987470219845974 48.91136942592806, "
        "2.3987235923275216 48.91136737662994, "
        "2.3979060659056546 48.91168224934015, "
        "2.397406540541382 48.911053256697016, "
        "2.3960346415227862 48.9094707629613, "
        "2.394971986925067 48.908402427906395, "
        "2.394600970312529 48.90804352203804, "
        "2.396341602487544 48.90758915531674, "
        "2.3945345171869423 48.905897450605906, "
        "2.394325892184115 48.905771374193044, "
        "2.393982916032293 48.90547018087834, "
        "2.3938724441682737 48.90534821538699, "
        "2.3937115304564407 48.90522599446579, "
        "2.3931054352481893 48.90467613680942, "
        "2.3919776498071688 48.90370636726724, "
        "2.3918870873484397 48.903636657106006, "
        "2.391803578444662 48.90354541005758, "
        "2.390724001813422 48.902539892650196, "
        "2.390399547375883 48.90217311993314, "
        "2.390001305291306 48.90181676753563, "
        "2.389350747720862 48.901224396468606, "
        "2.389265392805966 48.9011753984377, "
        "2.3890664926286718 48.90115369626973, "
        "2.3881681651210336 48.90133256474923, "
        "2.3855363917075874 48.90183349601605, "
        "2.3853111675769583 48.90184584618806, "
        "2.38478134502216 48.90223612301365, "
        "2.384154583744034 48.902405558868125, "
        "2.383348161299008 48.90265592184908, "
        "2.383387378573565 48.902800004465504, "
        "2.383516865513483 48.90326831961594, "
        "2.3837159433239776 48.9038520915594, "
        "2.383727455933841 48.90391600537917, "
        "2.3838973155659806 48.904896221580344, "
        "2.3831532978197054 48.90497945436384, "
        "2.3821228622202746 48.905078526079656, "
        "2.381782317400894 48.90493659541611, "
        "2.3816221737709156 48.905095842145556, "
        "2.3806398586559716 48.906020660814576, "
        "2.3802022151939206 48.90645636188217, "
        "2.3811115056745638 48.90639720899112, "
        "2.381768593124011 48.90804452121606, "
        "2.3819187251239136 48.9085181655703, "
        "2.381997604876444 48.90851453646528, "
        "2.382627019467677 48.908444285390296, "
        "2.382595667930333 48.908312503164126, "
        "2.383278179490456 48.90823605272432, "
        "2.3833454681462767 48.90836781473811, "
        "2.3836547106267787 48.90834195768212, "
        "2.38363747434373 48.90827812798061, "
        "2.383938901937376 48.908240941890774, "
        "2.383999947461837 48.90838300444458, "
        "2.384184247312064 48.90836234173792, "
        "2.3844145277434707 48.90910563596774, "
        "2.384834617870446 48.90905347420882, "
        "2.384834956843647 48.909128683052224, "
        "2.385006350229232 48.91009452619692, "
        "2.385010760221017 48.91047990791805, "
        "2.385025165568092 48.91051749364461, "
        "2.3850939083996163 48.910563516787285, "
        "2.3852514679265613 48.91063119590205, "
        "2.38507395634687 48.91083950247707, "
        "2.3849701513928654 48.91096396380781, "
        "2.383468119742854 48.91245358811226, "
        "2.382923836297029 48.91301824197535, "
        "2.3829985699739833 48.91304380916353, "
        "2.3830141161288227 48.91311492510806, "
        "2.3829745868717054 48.91357246980367, "
        "2.382933679599052 48.91379887772753, "
        "2.3820782484926615 48.91390869240205, "
        "2.382154242711308 48.913828152605085, "
        "2.381940946151328 48.91375059914561, "
        "2.3812736340181355 48.9124989247927, "
        "2.3811896081672255 48.91245082953529, "
        "2.381124954672553 48.91226614204778, "
        "2.3804955241197527 48.911157635701336, "
        "2.3819458521906385 48.910926809864684, "
        "2.382593773074414 48.91082403669066, "
        "2.382462021015946 48.91031255094373, "
        "2.382400729215769 48.91007481854895, "
        "2.3821688084670343 48.90933660618789, "
        "2.3815657150612646 48.90942694453383, "
        "2.381498399265183 48.90925502030999, "
        "2.3798834393441832 48.90943991192752, "
        "2.379642252985601 48.90866160357638, "
        "2.3785036223574743 48.908735106535936, "
        "2.378279091880934 48.90870455026466, "
        "2.378022205005743 48.90862316944599, "
        "2.377652283587552 48.908981873483036, "
        "2.376089623098615 48.91062217699082, "
        "2.375444149205392 48.91131487518983, "
        "2.3750136342847354 48.911830623663754, "
        "2.3748791054917096 48.91201158830447, "
        "2.3745283737007354 48.912587105081286, "
        "2.3739258992559873 48.913558798816666, "
        "2.3741201826330456 48.91362815738506, "
        "2.3742956494723586 48.91367404808213, "
        "2.37435423236441 48.91368153587155, "
        "2.374496188011009 48.91367599641446, "
        "2.3752650521799343 48.91361794033329, "
        "2.375659667788726 48.91358514597824, "
        "2.375680400174435 48.91410140671377, "
        "2.375788177926896 48.914091074186494, "
        "2.37585401868633 48.914404055912144, "
        "2.375610329561641 48.91440722683317, "
        "2.3756213448891703 48.914521508146215, "
        "2.375617532691521 48.914622265812234, "
        "2.3755313483784777 48.91462115831727, "
        "2.375557033956788 48.915210336356296, "
        "2.3750316029970087 48.91522017955213, "
        "2.3740298497115018 48.91524013182293, "
        "2.3719745431548946 48.91527525040331, "
        "2.3713549305773154 48.915286385930685, "
        "2.3712483461214786 48.91529931072659, "
        "2.368258993777263 48.91534863659704, "
        "2.3681397341457022 48.914503951611444, "
        "2.3680113124846276 48.913735870488445, "
        "2.367852787077442 48.91374808658441, "
        "2.367756657875707 48.9132408741125, "
        "2.3663387302117505 48.913375821396286, "
        "2.366547930929997 48.91448603267517, "
        "2.366465482287503 48.91449012378659, "
        "2.3662592847269637 48.91450355872737, "
        "2.366365812376172 48.9153855336051, "
        "2.364323601138035 48.91541925208244, "
        "2.3640820232596207 48.91542337123676, "
        "2.362906899544307 48.915429036468126, "
        "2.3628275811209387 48.91651732713469, "
        "2.3645866983149997 48.91666797518944, "
        "2.3646999612202495 48.9166676693485, "
        "2.365152333754909 48.916608020935115, "
        "2.3652672642011345 48.91781278945428, "
        "2.365303347238116 48.917875048486394, "
        "2.3654359179089846 48.917858651426464, "
        "2.3655533532390494 48.91785209155042, "
        "2.36615647665208 48.91785167406148, "
        "2.3663377890407746 48.91786523233371, "
        "2.3666750368658245 48.917851729238166, "
        "2.366939827050591 48.91784232626576, "
        "2.3684599339591945 48.91784045820644, "
        "2.3687889014996193 48.9178305153051, "
        "2.369377007612392 48.917830898189, "
        "2.369663448579412 48.91784140033592, "
        "2.370927441326264 48.917535583945245, "
        "2.3712789814902098 48.91759314624049, "
        "2.371358549648634 48.91758592331553, "
        "2.3713773884976237 48.91760759455782, "
        "2.37140860752046 48.91762035754146, "
        "2.3714971196114973 48.91763521248715, "
        "2.371804927046869 48.917684482483544, "
        "2.3723143579147274 48.917759094643145, "
        "2.372776115799277 48.917826267858025, "
        "2.372920264764812 48.91786659517549, "
        "2.3729875506797637 48.91783096817019, "
        "2.373030062682568 48.91781499786537, "
        "2.373551970551767 48.91764776036281, "
        "2.373709354515398 48.91760812550254, "
        "2.3737734398879855 48.91761115298799, "
        "2.374780272991995 48.917740525416185, "
        "2.374732674647971 48.917841896005605, "
        "2.3746504353494338 48.91809866266099, "
        "2.374531832948557 48.91865740904507, "
        "2.374485376198736 48.91877676418721, "
        "2.3744533202476203 48.91883146120889, "
        "2.3744104191866198 48.91888248641467, "
        "2.3742986128202936 48.918988016152035, "
        "2.3741718399597715 48.919090780499836, "
        "2.374024596720463 48.91919433885484, "
        "2.3735804159103946 48.919477087576176, "
        "2.3732420223155297 48.919701935490195, "
        "2.3729809207691974 48.91985436002659, "
        "2.3725016826325036 48.92010274967018, "
        "2.3723903794307257 48.92016602040189, "
        "2.3714657049020067 48.92119468122884, "
        "2.3703469020184773 48.92095715540077, "
        "2.370210990939168 48.920975725614355, "
        "2.3700548561115924 48.921132272762186, "
        "2.369889272884444 48.921277902901494, "
        "2.3697753820535694 48.92133126169846, "
        "2.368487030815677 48.92246749265828, "
        "2.367914867602146 48.92223690350334, "
        "2.367583151689137 48.92273071727473, "
        "2.367494288797157 48.92285524130738, "
        "2.3674339365635575 48.92299252569918, "
        "2.3673906753673783 48.9230723220002, "
        "2.3669952957297657 48.92371413817365, "
        "2.366233407656767 48.924818627903726, "
        "2.3659223908315603 48.925303820602814, "
        "2.3657913964209167 48.92552524926014, "
        "2.365658060732213 48.92571698326782, "
        "2.365369793038166 48.92607697814143, "
        "2.365254688717976 48.9262265486021, "
        "2.3649649537362922 48.92648490013233, "
        "2.364643935196324 48.92673321081932, "
        "2.3644979915937374 48.92683764874654, "
        "2.3641721254914754 48.92703466195235, "
        "2.3638246854150355 48.92721178967805, "
        "2.363636653315119 48.927297123336814, "
        "2.362982854450326 48.927525661551975, "
        "2.362747223239526 48.92759725138397, "
        "2.362617050711292 48.92763971969467, "
        "2.3623261025633133 48.927772180694525, "
        "2.3622452711159023 48.9277969109234, "
        "2.361806425599292 48.92785842789887, "
        "2.3615085416077224 48.927886517729085, "
        "2.3613239638845416 48.92791340857942, "
        "2.361262634410033 48.927907702133034, "
        "2.361152104085752 48.92790621184299, "
        "2.3608679355664837 48.92792897744974, "
        "2.3606550433877684 48.92793630773598, "
        "2.360383602074063 48.92791559638398, "
        "2.36099863002626 48.92873363026333, "
        "2.3611367474767992 48.92882340188745, "
        "2.3613893351922144 48.92892546520301, "
        "2.361648931987671 48.92901498242974, "
        "2.362164121851686 48.929226907888754, "
        "2.3639837391272964 48.92971805187713, "
        "2.3653087676609785 48.929939881251265, "
        "2.3653755257860434 48.92997004625397, "
        "2.365522339082229 48.93001847879772, "
        "2.3657891284902437 48.93007924951023, "
        "2.3665892418996823 48.93016441185418, "
        "2.3670506772395936 48.93020597976677, "
        "2.3671415639345983 48.930195587355286, "
        "2.3675225767862447 48.930076631820874, "
        "2.3686396863997787 48.92968062632464, "
        "2.369980450733151 48.92918946703978, "
        "2.370484795325172 48.92901675052695, "
        "2.3708673733849923 48.92886857999516, "
        "2.371604782942755 48.92860716746506, "
        "2.371952688679362 48.928504664642695, "
        "2.3747117948579484 48.927754710666264, "
        "2.3751044825098306 48.92768481220203, "
        "2.3752810401138826 48.92797259748821, "
        "2.375666550391851 48.92860052879253, "
        "2.376657240829061 48.93021090115187, "
        "2.3776443639401563 48.931893206831454, "
        "2.3775813819173255 48.93195938202017, "
        "2.3780378229304002 48.93290160509903, "
        "2.3781499695992907 48.932871555566635, "
        "2.378371479560334 48.932839434730404, "
        "2.3784684797526587 48.93283094316159, "
        "2.3785312006068544 48.93283666953446, "
        "2.3787352128793864 48.93289887154454, "
        "2.3788713239196406 48.93293106105435, "
        "2.3790010028241784 48.93292992550938, "
        "2.3796876626272074 48.93280579733776, "
        "2.379778346383554 48.93298431991254, "
        "2.3798146075590383 48.93303397008852, "
        "2.3798824322891563 48.933071184578566, "
        "2.3799902174266645 48.93307445088891, "
        "2.3803253785480245 48.93300962279263, "
        "2.381648521205688 48.93273588511253, "
        "2.3833109969004744 48.932391037249346, "
        "2.3837402706625137 48.9322812896818, "
        "2.3841326412579065 48.93273878601606, "
        "2.384181309044329 48.93271063845622, "
        "2.384381215528843 48.93257774385261, "
        "2.3843968455983697 48.93258082415758, "
        "2.3845374061934397 48.93249325060005, "
        "2.384491919818551 48.93231206086672, "
        "2.3854419565485983 48.932221076089654, "
        "2.3858424768757285 48.93253817970697, "
        "2.3860458735623085 48.93242486507979, "
        "2.386193973101014 48.932367166510566, "
        "2.386534769967004 48.93228796495701, "
        "2.3866619556090822 48.932266142777905, "
        "2.3867372702111425 48.93247696648013, "
        "2.3868506027923235 48.93282106447012, "
        "2.3868867487607615 48.93299570895791, "
        "2.3869558618217352 48.93315613707908, "
        "2.3870887863090773 48.93370257138579, "
        "2.390316084390133 48.933806653450645, "
        "2.3924118094565126 48.93389013298161, "
        "2.394140313621256 48.93397786571587, "
        "2.3943479964115006 48.93383156415266, "
        "2.3945228662713087 48.93368630508549, "
        "2.394575925640157 48.93362450634339, "
        "2.3953028455240712 48.93384242885732, "
        "2.3967000621476124 48.93394572972618, "
        "2.3968562601985957 48.93388181603967, "
        "2.3973364295691986 48.93422546108732, "
        "2.397624006696444 48.93425002740253, "
        "2.398041160424546 48.934164356883215, "
        "2.398500576097676 48.93413426769976, "
        "2.3997853851668727 48.93431995953842, "
        "2.400501186097011 48.93436693978104, "
        "2.4005403225122404 48.93442046121897, "
        "2.401169869884606 48.93422347119131, "
        "2.400339389583336 48.93314982604162, "
        "2.40049924978519 48.93310864183306, "
        "2.4000840272765056 48.93277653036955, "
        "2.3992604227626635 48.93211773274034, "
        "2.3989051322577746 48.93191721105689, "
        "2.3984094456513665 48.93158288215316, "
        "2.39724832280694 48.93084051656448, "
        "2.3967946885685363 48.930529793277756, "
        "2.39670556999953 48.93044751319733, "
        "2.396585987022041 48.93028412766542, "
        "2.3965465016356253 48.93015893697559, "
        "2.396528711918722 48.930045526457306, "
        "2.396612083259446 48.929564831255625, "
        "2.3966261005440423 48.929180904287044, "
        "2.396714720416719 48.92636388228789, "
        "2.3964236374527723 48.92627967819876, "
        "2.396307297950949 48.92630696654182, "
        "2.395538285171379 48.92648295146376, "
        "2.3953424830567673 48.92653772858803, "
        "2.3940610986217057 48.926996179816165, "
        "2.3932501086790126 48.92725647817645, "
        "2.3929563591166114 48.926934845142, "
        "2.3923152092993987 48.926089854447895, "
        "2.3901831647814973 48.926698621929155, "
        "2.3891603206195318 48.92698749102901, "
        "2.388298706581923 48.92725558615536, "
        "2.3857337585094194 48.927996072270616, "
        "2.3856867950007454 48.92792748371992, "
        "2.3853391752762585 48.92800843403449, "
        "2.3852307462504987 48.92759688981018, "
        "2.3849813951196706 48.92686989927154, "
        "2.384949900434512 48.92676541092136, "
        "2.3848038357125207 48.92665224619811, "
        "2.38470439886191 48.926519556096785, "
        "2.3843174670725853 48.92577204906754, "
        "2.3842998859083053 48.9257575682706, "
        "2.384651362903383 48.92569552040702, "
        "2.384655681863005 48.92544733808474, "
        "2.384631824690885 48.92527185365974, "
        "2.384562035215387 48.92505587558924, "
        "2.384353328413641 48.9250492026865, "
        "2.384251784399556 48.92463410357784, "
        "2.384289222755034 48.92458483306986, "
        "2.384273831047755 48.9245002294729, "
        "2.384196931008826 48.924425184014694, "
        "2.384116561817017 48.92441219344967, "
        "2.3840215300589365 48.924140999845, "
        "2.3841393284531347 48.924104746929125, "
        "2.3842171200895628 48.92408365002975, "
        "2.3842609806867308 48.92407632675787, "
        "2.3841842428750026 48.92387969946868, "
        "2.384109225317639 48.92386222553719, "
        "2.3840935656988282 48.92382105094637, "
        "2.3839451299866816 48.92381286871234, "
        "2.3838872220047906 48.92370581587343, "
        "2.383714846952958 48.92314783327033, "
        "2.383661764552086 48.92305999779941, "
        "2.38373004579746 48.92299488760448, "
        "2.3837755597000725 48.922913570113735, "
        "2.383801367079118 48.92279543308314, "
        "2.383650944580607 48.922592323633204, "
        "2.383600289334216 48.92249042301852, "
        "2.3833714161702417 48.92176531680858, "
        "2.3840935696870136 48.921627861554455, "
        "2.3847272716444796 48.92146923881355, "
        "2.3844183062840196 48.92070863934469, "
        "2.3842747819245416 48.92003702884539, "
        "2.384094619473979 48.91935530116825, "
        "2.3842495066735863 48.919349973061266, "
        "2.3855608732741054 48.91929001887703, "
        "2.3856769153228186 48.91928431164904, "
        "2.3864616709895894 48.91924397947784, "
        "2.386898336033722 48.9191565800508, "
        "2.3871061379403433 48.919126180429956, "
        "2.3871155559741206 48.9190209946896, "
        "2.3887138580872214 48.91782591102396, "
        "2.389284487660208 48.91733689796683, "
        "2.3893919263933716 48.91713599380057, "
        "2.389424408796953 48.91715865439051, "
        "2.3894618161431995 48.9172262923872, "
        "2.389554365725349 48.91759456786931, "
        "2.390071638273343 48.91893917684943, "
        "2.3930781803002104 48.91849205319328, "
        "2.3935051911041927 48.91872078432092, "
        "2.393646099272529 48.91929657413693, "
        "2.3935648911439062 48.91930828204295, "
        "2.393588474484704 48.919440058345074, "
        "2.393674289393642 48.919427197457416, "
        "2.3937828945590325 48.919832807823255, "
        "2.393772892845457 48.91998924004084, "
        "2.393829284428786 48.92018287206636, "
        "2.393894799671203 48.92018229701412, "
        "2.3939410968793657 48.92019242705278, "
        "2.393970953627618 48.9202060621065, "
        "2.394000579731238 48.9202395038637, "
        "2.394634067772495 48.92173642195275, "
        "2.395750732701247 48.92182120356551, "
        "2.397171086299102 48.921956944395454, "
        "2.3982618075955293 48.922044280687835, "
        "2.398081267658762 48.92160810318435, "
        "2.397350272041529 48.92015387399633, "
        "2.396912154098299 48.919220887934685, "
        "2.3969805571580376 48.91920415459882, "
        "2.3962524463139374 48.91833177297889, "
        "2.394464382197493 48.91837759198675, "
        "2.393777852658882 48.91839121946558, "
        "2.393821565668827 48.91825686985429, "
        "2.3939445439605795 48.91813755455895, "
        "2.394175586169834 48.918033575445186, "
        "2.3939370596113507 48.917689855547465, "
        "2.393537053472094 48.916923248488054, "
        "2.3930113627785974 48.917070767272065, "
        "2.392908900222187 48.91708283109402, "
        "2.3924886333059696 48.91583945837413, "
        "2.392684685034941 48.915800793273625, "
        "2.393271922223888 48.91565945814287, "
        "2.3933047938808647 48.91572533999275, "
        "2.3959227739749482 48.91505109614652, "
        "2.3962262857630265 48.91553122237121, "
        "2.3963099849214196 48.91560627337953, "
        "2.396654481839358 48.91602259448534, "
        "2.3968282361432336 48.9162186189524, "
        "2.396966449003624 48.91641986542109, "
        "2.3971833713202386 48.916656558783764, "
        "2.3983781008479204 48.916116704653234, "
        "2.3989556173114517 48.915849803050605, "
        "2.3997872442882366 48.915555417803375, "
        "2.39997616261672 48.91550149971376, "
        "2.4001580333004027 48.91546733240889, "
        "2.400256557196144 48.91544354459955, "
        "2.400430022870378 48.91540483471501, "
        "2.400517246742725 48.91553331334507, "
        "2.4014870862560653 48.9167671771753, "
        "2.402685566357709 48.91637117774408, "
        "2.403050707606014 48.91643079732164, "
        "2.403586024767232 48.917241838109035, "
        "2.4035190467417324 48.917393228639455, "
        "2.4033661311977745 48.91754363542067, "
        "2.4029131463710485 48.91759639952735, "
        "2.4026995145817227 48.917542623292555, "
        "2.4024711590643215 48.917601831030765, "
        "2.402355431745516 48.91755069534036, "
        "2.402188971732679 48.917606946832926, "
        "2.4021486315655065 48.91767198592026, "
        "2.4020527133833935 48.91765539005233, "
        "2.4017889765210705 48.91774195996434, "
        "2.4020119647335987 48.91799464055499, "
        "2.4021308032541318 48.918221845517245, "
        "2.4016409173377378 48.9182221086074, "
        "2.4014920519505996 48.91823394800391, "
        "2.401992951115204 48.91882420025286, "
        "2.402284651777753 48.919715688444235, "
        "2.402355568984292 48.92019854263117, "
        "2.401116735396456 48.92028260648421, "
        "2.401028635038368 48.91978844244259, "
        "2.400136692682292 48.919908352666404, "
        "2.4002477930783184 48.92004934994137, "
        "2.399971379103324 48.92014833808904, "
        "2.4011763193613564 48.921560874919706, "
        "2.4022029991856466 48.921234383498906, "
        "2.4021835218739716 48.921294141511474, "
        "2.401866788130309 48.92163820787138, "
        "2.401765334791674 48.92171857303252, "
        "2.4016263565344618 48.9217804213145, "
        "2.4020752342523095 48.92233634250308, "
        "2.401686256528177 48.92250050917948, "
        "2.401284024488543 48.92269773829275, "
        "2.4020927534119414 48.92367053541023, "
        "2.40221132507163 48.923632050986754, "
        "2.4027136897684236 48.92428532662533, "
        "2.401793528093291 48.92453230771327, "
        "2.401024303408097 48.92472991522567, "
        "2.4007586482554673 48.92480772640121, "
        "2.400585446737744 48.92491747288738, "
        "2.400491638907884 48.925005132290586, "
        "2.400459554920792 48.92506430876741, "
        "2.4006468082144474 48.9251578742558, "
        "2.4007611168666285 48.92518634194512, "
        "2.4009057429504863 48.92518885110212, "
        "2.4011093719822827 48.9251638021652, "
        "2.4019942025153265 48.925002749971405, "
        "2.402265188100248 48.92493485306368, "
        "2.402538781578103 48.92487866651876, "
        "2.402799791446683 48.924849384564126, "
        "2.4042845149430994 48.924854967458224, "
        "2.404935387709499 48.92486540480637, "
        "2.4053332863346526 48.92491504072208, "
        "2.4080716645446403 48.92520828742787, "
        "2.4082639362619536 48.925221819928716, "
        "2.4083935645065013 48.92522336108114, "
        "2.408650294794722 48.92521024328058, "
        "2.4110857216940467 48.92514309268874, "
        "2.4129714120303722 48.9250846559021, "
        "2.4136126728629574 48.92506556525673, "
        "2.4137370281835246 48.92505178870215, "
        "2.414084259999931 48.924999524284885, "
        "2.4143386941862004 48.92494500316793, "
        "2.4149148052518092 48.92480662728987, "
        "2.4152647240374256 48.92475618554174, "
        "2.4174802621649363 48.92409251460953, "
        "2.417745816542937 48.9240218422979, "
        "2.417826743976493 48.92398268473545)))",
    ),
]


def _format_qpv_tuple(qpv):
    code, name, infos, spec = qpv
    return {
        "code": code,
        "name": name,
        "communes_info": infos,
        "geometry": multipolygon_to_geometry(spec),
    }


def _params_for_random_qpv() -> dict:
    return _format_qpv_tuple(sample(QPVS, 1))


class QPVFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = QPV

    code = name = communes_info = geometry = None

    @classmethod
    def _adjust_kwargs(cls, **kwargs):
        if code := kwargs["code"]:
            [qpv] = filter(lambda qpv: qpv[0] == code, QPVS)
            return _format_qpv_tuple(qpv)
        return _params_for_random_qpv()
