var regExp = new RegExp( SearchParms.ContainingTextCustomParm );

function isValidLine( nLineNum, strText )
{
    var bIsValid = true;
    try
    {
        bIsValid = !regExp.test( strText );
    }
    catch( e )        {}
    return bIsValid;
}