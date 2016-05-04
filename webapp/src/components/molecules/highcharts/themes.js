export default {
  standard: {
    credits: { enabled: false },
    chart: {
      style: {
        fontFamily: "'proxima', 'Helvetica', sans-serif' ",
        paddingTop: '20px'  // Make room for buttons
      }
    },
    exporting: {
      buttons: {
        contextButton: {
          symbol: null,
          text: 'Export',
          x: -20,
          y: -30,
          theme: {
            style: {
              color: '#039',
              textDecoration: 'underline'
            }
          }
        }
      }
    },
    title: ''
  }
}
