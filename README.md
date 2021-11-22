# team5-server

1. 11/22 회의에 따라 결정된 사항에 맞추어 모델을 구성하였습니다.  
[회의록](https://www.notion.so/11-22-a46a2319f0694f7698ba3f755dbd80bb)에 기재된 사항과 동일합니다.  
회의록에 기재되지 않은 대댓글 기능은 일단은 ForeignKey를 활용하여 적어보긴 했는데, 코드 리뷰를 하실 때 주석을 참고해주시면 좋을 것 같습니다.  

2. User 모델은 마이그레이션하여 DB에 반영해두었고, User모델을 제외하고는 모두 주석처리 해두었습니다.  
다만, 모델들이 서로 관계를 맺고 있는 상황이라 모델 전체를 주석처리 할 수는 없었습니다. 따라서 이들을 빈 모델처럼 처리하여 마이그레이션 해두었습니다.  

3. image field를 활용하기 위해선 Pillow 라이브러리가 필요했습니다.  
requirements.txt에 포함해두긴 했는데 다른 환경에서도 제대로 다운로드가 가능할지 모르겠습니다.  
혹시 안된다면 알려주세요.  

4. 모델을 짜두기만 하고 실제 구동을 확인해보지를 못해서 이후에 수정할 사항이 많이 발견될 수 있습니다..ㅎㅎㅎ  
앞으로 열심히 발견해서 열심히 고치겠습니다,,  

그럼 편하게 피드백 주세요!😆
