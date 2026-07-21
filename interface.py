import streamlit as sl
import json
from issuer.authority import IssuerAuthority
from issuer.revocation import revCred
from holder.wallet import save_cred, load_cred, list_cred, del_cred
from holder.disclosure import showCred
from verifier.verify import verifyDisc

# UI Setup (basic layout and appeareance of the app)
sl.set_page_config(page_title='SeCreDiVer',layout='wide',page_icon='lock')

sl.title('Decentralized Credentials System :-') # heading
sl.markdown('selective disclosure and verification of credentials #Privacy&Trust')

# these blocks keep data saved even if the app refreshes
if 'authority' not in sl.session_state:
    sl.session_state.authority=None
if 'last_cred' not in sl.session_state:
    sl.session_state.last_cred={}
if 'last_disc' not in sl.session_state:
    sl.session_state.last_disc={}
if 'fields_buffer' not in sl.session_state:
    sl.session_state.fields_buffer=[]
if "found_creds" not in sl.session_state:
    sl.session_state.found_creds = []
# Logic for tracking selected credentials and user wallet contents
if "selected_cred" not in sl.session_state:
    sl.session_state.selected_cred = None
if "my_creds" not in sl.session_state:
    sl.session_state.my_creds=[]
if "disc" not in sl.session_state:
    sl.session_state.disc=None

# Dividing the app into three functional tabs for different roles
tab1,tab2,tab3=sl.tabs(['Issue','Owner','Verification'])

#  tab 1 - Issuer
with tab1:
    sl.subheader("Institution setup:")
    n=sl.text_input("Institute Name",placeholder='Eg; IIT Roorkee')     # input institute name
    if sl.button('SUBMIT'):
        if len(n)!=0:
            # Create a new authority (generates keys)
            sl.session_state.authority=IssuerAuthority(n)
            sl.session_state.fields_buffer.clear()
            sl.session_state.last_cred.clear()
            sl.session_state.last_disc.clear()
            sl.success('Institute successfully registered for issuing certificates !!')
        else:
            sl.warning("Institute registration can't be without a name !")
    sl.divider()
    if sl.session_state.authority is not None:
        sl.write("Institute: "+sl.session_state.authority.name)
        sl.write("Public key: "+sl.session_state.authority.getPubK())
    sl.divider()

    if sl.session_state.authority is not None:
        sl.subheader('Add credential fields:') 
        # Input institute name
        fn=sl.text_input('Field Name',placeholder='Eg; degree')
        ft=sl.radio('Enter the Type of the Value: ',['str','float','int','bool'])
        
        # Collecting field values based on the selected data type
        if len(fn)!=0:
            if ft=='str':
                fv=sl.text_input(fn,placeholder='Eg; degree')
            elif ft=='float':
                fv=sl.text_input(fn,placeholder='Eg; mean grade points')
            elif ft=='int':
                fv=sl.text_input(fn,placeholder='Eg; grade points')
            elif ft=='bool':
                fv=sl.radio(fn,[None,'True','False'])
                fv=True if fv=='True' else False if fv=='False' else None
            else:
                fv=None
            if ft!='bool' and len(fv)==0:
                fv=None
            # Handle empty input
            if sl.button('SUBMIT FIELDS'):
                if fv==None:
                    sl.warning(f"The {fn}'s value can't be an empty !")
                else:
                    try:
                        # Append processed field to the issuance buffer
                        sl.session_state.fields_buffer.append({
                            'name':fn,
                            'value':fv if ft=='str' else float(fv) if ft=='float' else int(fv) if ft=='int' else fv,
                            'ftype':ft
                        })
                        sl.success(fn+' added successfully !!')
                    except:
                        sl.error('Invalid data !!')
        sl.divider() 
        # Clear all added fields
        if len(sl.session_state.fields_buffer)!=0:
            if sl.button('CLEAR FIELDS'):
                sl.session_state.fields_buffer.clear()
            sl.divider()

        if len(sl.session_state.fields_buffer)!=0:
            sl.subheader('Issue credentials:')
            hn=sl.text_input("Enter Holder's Name",placeholder="Eg; Omkar")
            vd=sl.number_input("Days Of Validity",min_value=1,value=365)
            if sl.button('ISSUE CREDENTIALS'):
                tmp=dict()
                if len(hn)!=0:
                    for d in sl.session_state.fields_buffer:
                        tmp[d['name']]=d['value']
                    # Use the authority to sign the Merkle Root and issue the JSON
                    sl.session_state.last_cred=sl.session_state.authority.issueCred(hn,tmp,vd)
                    save_cred(sl.session_state.last_cred)
                    sl.success('Credential created successfully and saved in the wallet !!')
                else:
                    sl.warning("Credential holder's name can't be empty !")
        sl.divider()

    if len(sl.session_state.last_cred)!=0:
        sl.subheader('Issued Credentials:')
        sl.json(sl.session_state.last_cred)
# Tab 2: Holder
with tab2:
    sl.subheader("Check credentials:")
    chn=sl.text_input('Your Name',placeholder='Eg; Omkar')
    if sl.button("FIND MY CREDENTIALS"):
        sl.session_state.my_creds.clear()
        if len(chn)==0:
            sl.warning('Enter your name !')
        else:
            sl.session_state.my_creds.append(None)
            # Fetch available credentials from wallet
            for cred_id in list_cred():
                cred=load_cred(cred_id)
                if cred['holder']==chn:
                    sl.session_state.my_creds.append(cred_id)
            if len(sl.session_state.my_creds)==1:
                sl.error('No credentials by this name !!')
    
    if len(sl.session_state.my_creds)>1:
        sel_credID=sl.radio('Select the credential :-',sl.session_state.my_creds)
        if sl.button('LOAD CRED.'):
            if sel_credID==None:
                sl.warning('Select a cred. id to load !')
            else:
                sl.session_state.last_cred=load_cred(sel_credID)
                sl.success('Loaded credential successfully !!')
        if sl.button('DELETE CRED.'):
            if sel_credID==None:
                sl.warning('Select a credential to delete !')
            else:
                del_cred(sel_credID)
                sl.session_state.last_cred=dict()
                sl.success('Credential deleted successfully !!')
    sl.divider()

    sl.subheader('Create disclosure:')
    dn=sl.text_input("Enter the holder's name: ",placeholder='Eg; Omkar')
    if sl.button('FIND CRED.'):
        sl.session_state.found_creds.clear()
        if len(dn)!=0:
            for cid in list_cred():
                cl=load_cred(cid)
                if cl['holder']==dn:
                    sl.session_state.found_creds.append(cl)
            if len(sl.session_state.found_creds)==0:
                sl.warning("No certificates issued in your name !")
        else:
            sl.warning('Enter the name whose disclosure has to be created !')
    # Select credential
    if len(sl.session_state.found_creds)!=0:
        ina=sl.radio("Choose institute whose fields are to be viewed: ",[Cred['issuer'] for Cred in sl.session_state.found_creds])
        for c in sl.session_state.found_creds:
            if c['issuer']==ina:
                sl.session_state.last_cred=c
                break
    #select fields to reveal
    if len(sl.session_state.last_cred)!=0:
        nl=[field['name'] for field in sl.session_state.last_cred['fields']]
        revel=list()
        sl.write(*nl)
        # Choosing specific data points to share with the verifier
        no=sl.text_input('Enter the fields indices to which are to be revealed: ',placeholder="Eg; '0 3 5' etc.").split()
        for i in range(len(no)):
            revel.append(nl[int(no[i])])
        if sl.button('SUBMIT QUERY'):
            # Generate the Merkle Proofs for the chosen fields
            sl.session_state.last_disc=showCred(sl.session_state.last_cred,revel)
            sl.success('Successfully created disclosure !!')
    sl.divider()

    if len(sl.session_state.last_disc)!=0:
        sl.subheader("Disclosure Operations:")
        sl.json(sl.session_state.last_disc)
        sl.download_button('Download disc.',json.dumps(sl.session_state.last_disc,indent=2),'disclosure.json','application/json')
        sl.divider()

# Tab 3: verifier
with tab3:
    sl.subheader('Verify Disclosure:')
    # Uploading the selctive disclosed JSON for verifing
    upl=sl.file_uploader('Upload Disclosure JSON:',type=['json'])
    if upl is not None:
        try:
            sl.session_state.disc=json.loads(upl.getvalue().decode())
            sl.success('Disclosure loaded successfully !!')
            sl.json(sl.session_state.disc)
        except:
            sl.error('Invalid JSON file !!')
    else:
        sl.info('Upload a disclosure JSON file to verify !')
    
    if sl.button('VERIFY'):
        if sl.session_state.disc is not None:
            # verifing the merkle Root, signature, expiry, and revocation status
            res,reason=verifyDisc(sl.session_state.disc)
            if res:
                sl.success('Valid Disclosure !! -- '+reason)
                sl.subheader('Revealed Fields:')
                for item in sl.session_state.disc['revealed']:
                    sl.write(item['name']+' : '+str(item['value']))
                sl.write('Issued at: '+sl.session_state.disc['issued_at'])
                sl.write('Expires at: '+sl.session_state.disc['expires_at'])
                sl.write('Hidden fields: '+str(list(sl.session_state.disc['hidden'].keys())))
            else:
                sl.error('Invalid Disclosure !! -- '+reason)
        else:
            sl.warning('Upload a file first!!')
    sl.divider()

# revocation function
sl.divider()
with sl.expander('Revoke a Credential:'):
    rh=sl.text_input('Enter Credential Root Hex:',placeholder='Eg; a3f19c2d...')
    if sl.button('REVOKE'):
        if len(rh)==0:
            sl.warning('Enter the credential root hex !')
        elif len(rh)!=64:
            sl.warning('Root hex must be 64 characters !')
        else:
            # Blacklist the root hash to prevent further valid verification
            revCred(rh)
            sl.success('Credential revoked successfully !!')
            sl.info('Revoked root: '+rh)
