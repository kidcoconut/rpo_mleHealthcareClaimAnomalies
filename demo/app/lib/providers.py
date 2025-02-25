import pandas as pd
import lib.utils as libPaths
import lib.claims as libClaims

from lib.models import mdl_utils, mdl_xgb, mdl_logR, mdl_svm
from lib.models import mdl_autoenc, mdl_kmeans
import sys

m_blnTraceOn = True
m_blnTrace2On = False

#--- load, merge data from file
m_kstrDataPath = libPaths.pth_data
m_kstrModelPath = libPaths.pth_model
m_kstrBinModelPath = libPaths.pth_binModels



def load_providers(blnIsTrain=False):

    pdfClaims = libClaims.loadPkl_claims(blnIsTrain)
    pdfClaims = pdfClaims.drop(['ClmProcedureCode_1', 'ClmProcedureCode_2', 'ClmProcedureCode_3', 
                            'ClmProcedureCode_4', 'ClmProcedureCode_5', 'ClmProcedureCode_6',
                            'Gender', 'Race', 'County'], axis=1)
    pdfProviders = pdfClaims.groupby(['Provider'], as_index=False).agg('sum')
    return pdfProviders


#--- feat eng
def do_featEng(pdfClaimsFeatEng, blnIsTrain=False):
    if (m_blnTraceOn): print("TRACE (providers.doFeatEng):  blnIsTrain, ", blnIsTrain)
    pdfFeatEng = pdfClaimsFeatEng

    #--- add new features to assist with predictions
    pdfFeatEng['InscClaimReimbursement_ProviderAvg'] = pdfFeatEng.groupby(['Provider'])['InscClaimAmtReimbursed'].transform('mean') 
    pdfFeatEng['DeductibleAmtPaid_ProviderAvg'] = pdfFeatEng.groupby(['Provider'])['DeductibleAmtPaid'].transform('mean')
    
    pdfFeatEng['IPAnnualReimbursementAmt_ProviderAvg'] = pdfFeatEng.groupby(['Provider'])['IPAnnualReimbursementAmt'].transform('mean')
    pdfFeatEng['IPAnnualDeductibleAmt_ProviderAvg'] = pdfFeatEng.groupby(['Provider'])['IPAnnualDeductibleAmt'].transform('mean')

    pdfFeatEng['OPAnnualReimbursementAmt_ProviderAvg'] = pdfFeatEng.groupby(['Provider'])['OPAnnualReimbursementAmt'].transform('mean')
    pdfFeatEng['OPAnnualDeductibleAmt_ProviderAvg'] = pdfFeatEng.groupby(['Provider'])['OPAnnualDeductibleAmt'].transform('mean')
    return pdfFeatEng



def get_logrPredict(pdfTestClaims):

    #--- logistic regression predictions;  load test data
    pdfClaims = pdfTestClaims
    #print("INFO (providers.get_logrPredict)  pdfClaims.shape):  ", pdfClaims.shape)

    pdfFeatEng = do_featEng(pdfClaims, False)
    npaScaled = mdl_utils.doProviders_stdScaler(pdfFeatEng, False)
    pdfScaled = mdl_utils.doProviders_stdScaler_toPdf(npaScaled)
    #print("INFO (predict.npaScaled.shape):  ", npaScaled.shape)

    ndaPredict = mdl_logR.predict(npaScaled)
    #print("INFO (predict.npaPredict.shape):  ", ndaPredict.shape)

    pdfPredict = pd.DataFrame(ndaPredict)
    #print("INFO (predict.pdfPredict.shape):  ", pdfPredict.shape)

    #--- stitch the grouped data with the labels
    pdfResults = pdfFeatEng.groupby(['Provider'], as_index=False).agg('sum')
    #print("INFO (predict.pdfGrpFeatEng.shape):  ", pdfResults.shape)

    pdfResults.insert(0, "hasAnom?", pdfPredict[0])
    return pdfResults    


def get_svmPredict(pdfTestClaims):

    #--- support vector machine predictions;  load test data
    pdfClaims = pdfTestClaims
    if (m_blnTraceOn):  print("TRACE (providers.get_svmPredict) pdfClaims.shape:  ", pdfClaims.shape)

    pdfFeatEng = do_featEng(pdfClaims, False)
    npaScaled = mdl_utils.doProviders_stdScaler(pdfFeatEng, False)
    pdfScaled = mdl_utils.doProviders_stdScaler_toPdf(npaScaled)
    if (m_blnTraceOn):  print("TRACE (providers.get_svmPredict) npaScaled.shape:  ", npaScaled.shape)

    ndaPredict = mdl_svm.predict(npaScaled)
    if (m_blnTraceOn):  print("TRACE (providers.get_svmPredict) npaPredict.shape:  ", ndaPredict.shape)

    pdfPredict = pd.DataFrame(ndaPredict)
    if (m_blnTraceOn):  print("TRACE (providers.get_svmPredict) pdfPredict.shape:  ", pdfPredict.shape)

    #--- stitch the grouped data with the labels
    pdfResults = pdfFeatEng.groupby(['Provider'], as_index=False).agg('sum')
    if (m_blnTraceOn):  print("TRACE (providers.get_svmPredict) pdfResults.shape:  ", pdfResults.shape)

    pdfResults.insert(0, "hasAnom?", pdfPredict[0])
    return pdfResults    



def get_xgbPredict(pdfTestClaims):

    try:
        #--- load test data
        pdfClaims = pdfTestClaims
        if (m_blnTrace2On):  print("TRACE (providers.get_xgbPredict)  pdfClaims.shape):  ", pdfClaims.shape)

        if (m_blnTrace2On):  print("TRACE (providers.get_xgbPredict) doFeatEng (provider) ... ")
        pdfFeatEng = do_featEng(pdfClaims, False)

        if (m_blnTrace2On):  print("TRACE (providers.get_xgbPredict) doStdScaler ... ")
        npaScaled = mdl_utils.doProviders_stdScaler(pdfFeatEng, False)

        if (m_blnTrace2On):  print("TRACE (providers.get_xgbPredict) doStdScaler_toPdf ... ")
        pdfScaled = mdl_utils.doProviders_stdScaler_toPdf(npaScaled)
        #if (m_blnTraceOn):  print("TRACE (predict.npaScaled.shape1):  ", npaScaled.shape)

        if (m_blnTrace2On):  print("TRACE (providers.get_xgbPredict) run prediction ... ")
        ndaPredict = mdl_xgb.predict(npaScaled)
        #if (m_blnTraceOn):  print("TRACE (predict.npaPredict.shape2):  ", ndaPredict.shape)

        if (m_blnTrace2On):  print("TRACE (providers.get_xgbPredict) convert to dataframe ... ")
        pdfPredict = pd.DataFrame(ndaPredict)
        pdfAnoms = pdfPredict[pdfPredict[0] > 0]
        if (m_blnTrace2On):  print("TRACE (providers.get_xgbPredict) pdfPredict.shape:  ", pdfPredict.shape)
        if (m_blnTraceOn):  print("TRACE (providers.get_xgbPredict) #anoms:  ", len(pdfAnoms.index))

        #--- group data by provider
        if (m_blnTrace2On):  print("TRACE (providers.get_xgbPredict) group claims by provider ... ")
        pdfResults = pdfFeatEng.groupby(['Provider'], as_index=False).agg('sum')
        if (m_blnTrace2On):  print("TRACE (providers.get_xgbPredict) pdfResults.shape:  ", pdfResults.shape)

        #--- stitch the grouped data with the labels
        if (m_blnTrace2On):  print("TRACE (providers.get_xgbPredict) merge labels into dataset ... ")
        pdfResults.insert(0, "hasAnom?", pdfPredict[0])

    except:
        e = sys.exc_info()
        print("ERROR (providers.get_xgbPredict_genError):  ", e)  
    
    
    if (m_blnTraceOn):  print("TRACE (providers.get_xgbPredict) proc complete; return ... ")
    return pdfResults



def get_encPredict(pdfTestClaims):

    #--- principal component analysis predictions;  load test data
    pdfClaims = pdfTestClaims
    if (m_blnTraceOn):  print("TRACE (providers.get_encPredict) ppdfClaims.shape:  ", pdfClaims.shape)

    pdfFeatEng = do_featEng(pdfClaims, False)                           #--- not grouped by provider
    

    #--- perform standard scaling; get fit then transform                      
    npaScaled = mdl_utils.doProviders_stdScaler(pdfFeatEng, False)               #--- grouped by provider
    pdfScaled = mdl_utils.doProviders_stdScaler_toPdf(npaScaled)
    #print("INFO (predict.npaScaled.shape):  ", npaScaled.shape)

    #--- perform PCA; then autoencode predict
    ndaPredict = mdl_autoenc.predict(pdfScaled)
    #print("INFO (predict.npaPredict.shape):  ", ndaPredict.shape)

    pdfPredict = pd.DataFrame(ndaPredict)
    #print("INFO (predict.pdfPredict.shape):  ", pdfPredict.shape)

    #--- stitch the grouped data with the labels
    pdfResults = pdfFeatEng.groupby(['Provider'], as_index=False).agg('sum')
    #print("INFO (predict.pdfGrpFeatEng.shape):  ", pdfResults.shape)

    pdfResults.insert(0, "hasAnom?", pdfPredict[0])
    return pdfResults    
