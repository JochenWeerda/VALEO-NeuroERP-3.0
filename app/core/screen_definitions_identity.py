"""Identity administration as native ScreenDefinitions, using the shared builder."""

def base(screen_id: str,title: str,endpoint: str,columns: list[dict]) -> dict:
    return {'schemaVersion':1,'id':screen_id,'domain':'platform','mode':'list','title':title,
        'subtitle':'Identität und Ressourcen','adapter':{'type':'native','sourceId':screen_id,'temporary':False},
        'layout':{'floorplan':'worklist','density':'compact','contextRail':'audit','tableProfile':'audit'},
        'dataSources':[{'key':'entity','endpoint':'/api/v1/identity/session'},
                       {'key':'records','endpoint':endpoint,'pageSize':50,'staleTimeMs':5000}],
        'summary':[{'key':'tenant_id','label':'Aktiver Mandant','kind':'identity'},
                   {'key':'subject','label':'Angemeldete Kennung','kind':'identity'}],
        'tables':[{'key':'records','label':title,'dataSourceKey':'records','serverPagination':False,
            'pageSize':50,'virtualized':True,'rowHeight':44,'columns':columns}],
        'noWorkflowReason':'Administrative Kapazitätsverwaltung ohne fachlichen Belegworkflow.',
        'noProcessChainReason':'Identität und Kontingente sind Plattformverwaltung, keine ERP-Belegkette.',
        'performance':{'initialPayloadBudgetKb':50,'requiresLazyTabs':False,'requiresVirtualTables':True,
                       'lookupMinChars':2,'bundleGroup':'platform'},
        'agentContract':{'businessPurpose':title,'sensitiveFields':['owner','subject','actor'],
            'forbiddenAgentTasks':['Plattformkontingente erhöhen','Kontingente anderer Mandanten einsehen'],
            'testSelectors':{'screenRoot':'[data-testid="'+screen_id.replace('/','-')+'"]'}}}


def budget_screen() -> dict:
    screen=base('admin/identity-budgets','Nutzer- und Agentenkontingente','/api/v1/identity/budgets',[
        {'key':'id','label':'Kontingent-ID','width':180,'filterable':True},
        {'key':'owner','label':'Empfänger','width':180,'filterable':True},
        {'key':'kind','label':'Art','width':90,'filterable':True},
        *[{'key':key,'label':label,'width':110,'renderKind':'number','sortable':True} for key,label in
          [('limit','Tokens gesamt'),('allocated','Unterbudgets'),('reserved','Reserviert'),
           ('spent','Eigener Verbrauch'),('total_spent','Verbrauch inkl. Kinder'),('available','Verfügbar'),
           ('max_children','Max. Unterkontingente'),('children','Vergeben')]],
        {'key':'parent','label':'Elternkontingent','width':180}])
    quantities=[{'key':'tokens','label':'Token-Kontingent','type':'number','required':True},
                {'key':'max_children','label':'Maximale Anzahl direkter Unterkontingente','type':'number','required':True}]
    def action(key,label,permission,fields,kind):
        return {'key':key,'label':label,'command':'identity.budget.'+key,'kind':kind,'zone':'header',
                'dangerLevel':'moderate','requiresConfirmation':True,'auditReasonRequired':True,
                'humanApprovalRequired':True,'forbiddenForAgents':True,'permission':permission,
                'method':'POST','commandEndpoint':'/api/v1/identity/budgets/actions/'+key,'inputFields':fields}
    screen['actions']=[
        action('allocate','Kontingent vergeben','identity:quota:allocate',[
            {'key':'parent','label':'Elternkontingent-ID','type':'text','required':True},
            {'key':'owner','label':'Empfängerkennung','type':'text','required':True},
            {'key':'kind','label':'Empfängerart','type':'select','required':True,
             'options':[{'value':'user','label':'Nutzer'},{'value':'agent','label':'Agent'}]},
            {'key':'request_id','label':'Vergabereferenz','type':'text','required':True,
             'helpText':'Bei Wiederholung dieselbe Referenz verwenden; abweichende Eingaben werden abgewiesen.'},
            *quantities],'primary'),
        action('root','Mandantenbudget bereitstellen','platform:quota:manage',quantities,'secondary'),
        {'key':'ledger','label':'Verbrauchsnebenbuch','kind':'secondary','zone':'header','dangerLevel':'safe',
         'permission':'identity:quota:read','navigationRoute':'/admin/token-consumption','command':'identity.ledger.open'}]
    return screen


def ledger_screen() -> dict:
    screen=base('admin/token-consumption','Technisches Verbrauchsnebenbuch','/api/v1/identity/consumption-ledger',[
        {'key':'id','label':'Eintrag','width':160},
        {'key':'event','label':'Vorgang','width':180,'filterable':True},
        {'key':'actor','label':'Verifizierte Kennung','width':180,'filterable':True},
        {'key':'at','label':'Zeitpunkt','width':170,'renderKind':'datetime','sortable':True},
        {'key':'tokens','label':'Tokenmenge','width':110,'renderKind':'number'},
        {'key':'actual_tokens','label':'Verbraucht','width':110,'renderKind':'number'},
        {'key':'job','label':'Auftrag','width':180},
        {'key':'budget_id','label':'Kontingent','width':180},
        {'key':'reason','label':'Begründung','width':220}])
    screen['subtitle']='Tokenmengen und Zuordnung; Geldwerte benötigen hinterlegte Preise'
    screen['actions']=[{'key':'budgets','label':'Kontingente öffnen','kind':'primary','zone':'header',
        'dangerLevel':'safe','permission':'identity:quota:read','navigationRoute':'/admin/identity-budgets','command':'identity.budgets.open'}]
    return screen


IDENTITY_SCREEN_BUILDERS={'admin/identity-budgets':budget_screen,'admin/token-consumption':ledger_screen}
