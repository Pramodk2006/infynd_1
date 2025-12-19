import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import './EnhancedSummaryCard.css';

const EnhancedSummaryCard = () => {
  const { companyName } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState('card'); // 'card' or 'table'

  useEffect(() => {
    fetchEnhancedData();
  }, [companyName]);

  const fetchEnhancedData = async () => {
    setLoading(true);
    setError(null);

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 60000); // 60 second timeout

      const response = await fetch(`http://localhost:5000/api/companies/${companyName}/enhanced`, {
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        if (response.status === 202) {
          setError('Summary is still being prepared. Please check the Summaries page.');
          return;
        }
        throw new Error(`Failed to fetch: ${response.status}`);
      }

      const result = await response.json();
      setData(result);
    } catch (err) {
      if (err.name === 'AbortError') {
        setError('Request timed out. The summary may still be preparing.');
      } else {
        setError(err.message);
      }
    } finally {
      setLoading(false);
    }
  };

  // Helper to extract value from enhanced field object or return primitive directly
  const getFieldValue = (field) => {
    if (field === null || field === undefined) return null;
    if (typeof field === 'object' && field !== null && 'value' in field) {
      return field.value;
    }
    return field;
  };

  if (loading) {
    return (
      <div className="enhanced-card-loading">
        <div className="spinner"></div>
        <p>Extracting comprehensive company data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="enhanced-card-error">
        <p>Error: {error}</p>
        <button onClick={fetchEnhancedData}>Retry</button>
      </div>
    );
  }

  if (!data) return null;

  const downloadCSV = () => {
    // Prepare CSV data
    const csvRows = [];

    // Add header
    csvRows.push('Field,Value');

    // Add basic fields
    const basicFields = [
      ['Domain', getFieldValue(data.domain)],
      ['Domain Status', getFieldValue(data.domain_status)],
      ['Company Registration Number', getFieldValue(data.company_registration_number)],
      ['VAT Number', getFieldValue(data.vat_number)],
      ['Company Name', getFieldValue(data.company_name)],
      ['Acronym', getFieldValue(data.acronym)],
      ['Logo URL', getFieldValue(data.logo_url)],
      ['Full Address', getFieldValue(data.full_address)],
      ['Phone', getFieldValue(data.phone)],
      ['Sales Phone', getFieldValue(data.sales_phone)],
      ['Fax', getFieldValue(data.fax)],
      ['Mobile', getFieldValue(data.mobile)],
      ['Other Numbers', getFieldValue(data.other_numbers)?.join('; ')],
      ['Email', getFieldValue(data.email)],
      ['All Emails', getFieldValue(data.all_emails)?.join('; ')],
      ['Hours of Operation', getFieldValue(data.hours_of_operation)],
      ['HQ Indicator', getFieldValue(data.hq_indicator) ? 'Yes' : 'No'],
      ['Sector', getFieldValue(data.sector)],
      ['Industry', getFieldValue(data.industry)],
      ['Sub-Industry', getFieldValue(data.sub_industry)],
      ['SIC Code', getFieldValue(data.sic_code)],
      ['SIC Description', getFieldValue(data.sic_text)],
      ['Tags', getFieldValue(data.tags)?.join('; ')],
      ['Certifications', getFieldValue(data.certifications)?.join('; ')],
      ['Short Description', getFieldValue(data.short_description)],
      ['Long Description', getFieldValue(data.long_description)],
      ['Executive Summary', getFieldValue(data.generated_summary)],
      ['Extraction Timestamp', new Date(getFieldValue(data.extraction_timestamp)).toLocaleString()],
      ['Text Length', getFieldValue(data.text_length) + ' characters'],
    ];

    basicFields.forEach(([field, value]) => {
      if (value && value !== '-') {
        // Escape quotes and wrap in quotes if contains comma or newline
        const escapedValue = String(value).replace(/"/g, '""');
        const finalValue = escapedValue.includes(',') || escapedValue.includes('\n')
          ? `"${escapedValue}"`
          : escapedValue;
        csvRows.push(`"${field}",${finalValue}`);
      }
    });


    // Add people section
    const people = getFieldValue(data.people);
    if (people && people.length > 0 && getFieldValue(people[0].name) !== '-') {
      csvRows.push(''); // Empty row for separation
      csvRows.push('Team Members');
      csvRows.push('Domain,Name,Title,Email,Profile URL');
      people.forEach(person => {
        const row = [
          getFieldValue(data.domain),
          getFieldValue(person.name),
          getFieldValue(person.title),
          getFieldValue(person.email) !== '-' ? getFieldValue(person.email) : '',
          getFieldValue(person.url) !== '-' ? getFieldValue(person.url) : ''
        ].map(val => {
          const escaped = String(val).replace(/"/g, '""');
          return escaped.includes(',') ? `"${escaped}"` : escaped;
        });
        csvRows.push(row.join(','));
      });
    }

    // Add certifications section
    const certifications = getFieldValue(data.certifications);
    if (certifications && certifications.length > 0 && certifications[0] !== '-') {
      csvRows.push(''); // Empty row for separation
      csvRows.push('Certifications');
      csvRows.push('Domain,Certification');
      certifications.forEach(cert => {
        const row = [
          getFieldValue(data.domain),
          cert
        ].map(val => {
          const escaped = String(val).replace(/"/g, '""');
          return escaped.includes(',') ? `"${escaped}"` : escaped;
        });
        csvRows.push(row.join(','));
      });
    }

    // Add services section
    const services = getFieldValue(data.services);
    if (services && services.length > 0 && getFieldValue(services[0].service) !== '-') {
      csvRows.push(''); // Empty row for separation
      csvRows.push('Services & Solutions');
      csvRows.push('Domain,Service,Type');
      services.forEach(service => {
        const row = [
          getFieldValue(data.domain),
          getFieldValue(service.service),
          getFieldValue(service.type)
        ].map(val => {
          const escaped = String(val).replace(/"/g, '""');
          return escaped.includes(',') ? `"${escaped}"` : escaped;
        });
        csvRows.push(row.join(','));
      });
    }

    // Create CSV content
    const csvContent = csvRows.join('\n');

    // Create blob and download
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);

    link.setAttribute('href', url);
    link.setAttribute('download', `${getFieldValue(data.company_name)}_summary_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const renderTableView = () => {
    const allFields = [
      { label: 'Company Name', value: getFieldValue(data.company_name) },
      { label: 'Acronym', value: getFieldValue(data.acronym) },
      { label: 'Domain', value: getFieldValue(data.domain) },
      { label: 'Domain Status', value: getFieldValue(data.domain_status) },
      { label: 'Logo URL', value: getFieldValue(data.logo_url), type: 'link' },
      { label: 'Executive Summary', value: getFieldValue(data.generated_summary) },
      { label: 'Short Description', value: getFieldValue(data.short_description) },
      { label: 'Long Description', value: getFieldValue(data.long_description) },
      { label: 'Sector', value: getFieldValue(data.sector) },
      { label: 'Industry', value: getFieldValue(data.industry) },
      { label: 'Sub-Industry', value: getFieldValue(data.sub_industry) },
      { label: 'SIC Code', value: getFieldValue(data.sic_code) },
      { label: 'SIC Description', value: getFieldValue(data.sic_text) },
      { label: 'Tags', value: getFieldValue(data.tags)?.join(', ') },
      { label: 'Company Registration Number', value: getFieldValue(data.company_registration_number) },
      { label: 'VAT Number', value: getFieldValue(data.vat_number) },
      { label: 'Full Address', value: getFieldValue(data.full_address) },
      { label: 'Phone', value: getFieldValue(data.phone) },
      { label: 'Sales Phone', value: getFieldValue(data.sales_phone) },
      { label: 'Fax', value: getFieldValue(data.fax) },
      { label: 'Mobile', value: getFieldValue(data.mobile) },
      { label: 'Email', value: getFieldValue(data.email), type: 'email' },
      { label: 'All Emails', value: getFieldValue(data.all_emails)?.join(', ') },
      { label: 'Other Numbers', value: getFieldValue(data.other_numbers)?.join(', ') },
      { label: 'Hours of Operation', value: getFieldValue(data.hours_of_operation) },
      { label: 'HQ Indicator', value: getFieldValue(data.hq_indicator) ? 'Yes' : 'No' },
      { label: 'Certifications', value: getFieldValue(data.certifications)?.join(', ') },
      { label: 'Extraction Timestamp', value: new Date(getFieldValue(data.extraction_timestamp)).toLocaleString() },
      { label: 'Text Length', value: getFieldValue(data.text_length)?.toLocaleString() + ' characters' },
    ];

    const people = getFieldValue(data.people);
    const services = getFieldValue(data.services);

    return (
      <div className="table-view-container">
        <table className="summary-table-view">
          <thead>
            <tr>
              <th>Field</th>
              <th>Value</th>
            </tr>
          </thead>
          <tbody>
            {allFields.map((field, idx) => (
              field.value && field.value !== '-' && (
                <tr key={idx}>
                  <td className="field-label">{field.label}</td>
                  <td className="field-value">
                    {field.type === 'email' ? (
                      <a href={`mailto:${field.value}`}>{field.value}</a>
                    ) : field.type === 'link' ? (
                      <a href={field.value} target="_blank" rel="noopener noreferrer">{field.value}</a>
                    ) : (
                      field.value
                    )}
                  </td>
                </tr>
              )
            ))}

            {/* People Section */}
            {people && people.length > 0 && getFieldValue(people[0].name) !== '-' && (
              <tr>
                <td className="field-label">Team Members</td>
                <td className="field-value">
                  <table className="nested-table">
                    <thead>
                      <tr>
                        <th>Name</th>
                        <th>Title</th>
                        <th>Email</th>
                        <th>Profile URL</th>
                      </tr>
                    </thead>
                    <tbody>
                      {people.map((person, idx) => (
                        <tr key={idx}>
                          <td>{getFieldValue(person.name)}</td>
                          <td>{getFieldValue(person.title)}</td>
                          <td>{getFieldValue(person.email) !== '-' ? <a href={`mailto:${getFieldValue(person.email)}`}>{getFieldValue(person.email)}</a> : '-'}</td>
                          <td>{getFieldValue(person.url) !== '-' ? <a href={getFieldValue(person.url)} target="_blank" rel="noopener noreferrer">View</a> : '-'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </td>
              </tr>
            )}

            {/* Services Section */}
            {services && services.length > 0 && getFieldValue(services[0].service) !== '-' && (
              <tr>
                <td className="field-label">Services & Solutions</td>
                <td className="field-value">
                  <table className="nested-table">
                    <thead>
                      <tr>
                        <th>Service</th>
                        <th>Type</th>
                      </tr>
                    </thead>
                    <tbody>
                      {services.map((service, idx) => (
                        <tr key={idx}>
                          <td>{getFieldValue(service.service)}</td>
                          <td><span className={`service-type-badge ${getFieldValue(service.type).toLowerCase()}`}>{getFieldValue(service.type)}</span></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    );
  };

  return (
    <div className="enhanced-summary-card">
      {/* View Toggle and Download Buttons */}
      <div className="view-toggle-container">
        <div className="view-buttons">
          <button
            className={`view-toggle-btn ${viewMode === 'card' ? 'active' : ''}`}
            onClick={() => setViewMode('card')}
          >
            Card View
          </button>
          <button
            className={`view-toggle-btn ${viewMode === 'table' ? 'active' : ''}`}
            onClick={() => setViewMode('table')}
          >
            Table View
          </button>
        </div>
        <button
          className="download-csv-btn"
          onClick={downloadCSV}
          title="Download as CSV"
        >
          📥 Download CSV
        </button>
      </div>

      {viewMode === 'table' ? renderTableView() : (
        <div className="card-view-container">
          {/* Header Section */}
          <div className="card-header">
            <div className="company-identity">
              {getFieldValue(data.logo_url) && getFieldValue(data.logo_url) !== '-' && (
                <img src={getFieldValue(data.logo_url)} alt={`${getFieldValue(data.company_name)} logo`} className="company-logo" />
              )}
              <div className="company-title">
                <h1>{getFieldValue(data.company_name)}</h1>
                {getFieldValue(data.acronym) && getFieldValue(data.acronym) !== '-' && (
                  <span className="acronym">{getFieldValue(data.acronym)}</span>
                )}
                <a href={`https://${getFieldValue(data.domain)}`} target="_blank" rel="noopener noreferrer" className="domain-link">
                  {getFieldValue(data.domain)}
                </a>
              </div>
            </div>
            <div className="status-badge">
              <span className={`badge ${getFieldValue(data.domain_status)}`}>{getFieldValue(data.domain_status)}</span>
            </div>
          </div>

          {/* Description Section */}
          <div className="card-section description-section">
            <h2>Description</h2>
            {getFieldValue(data.short_description) && getFieldValue(data.short_description) !== '-' && (
              <div className="short-description-box" style={{
                backgroundColor: '#f8f9fa',
                borderLeft: '4px solid #007bff',
                padding: '15px',
                marginBottom: '20px',
                fontSize: '1.2em',
                lineHeight: '1.5',
                color: '#2c3e50'
              }}>
                <strong>One-Liner:</strong> {getFieldValue(data.short_description)}
              </div>
            )}

            {getFieldValue(data.generated_summary) && getFieldValue(data.generated_summary) !== '-' && (
              <div className="generated-summary" style={{ marginBottom: '15px' }}>
                <h3 style={{ fontSize: '1.1em', color: '#666', marginTop: '0' }}>Executive Summary</h3>
                <p style={{ lineHeight: '1.6', whiteSpace: 'pre-line' }}>{getFieldValue(data.generated_summary)}</p>
              </div>
            )}

            <p className="long-desc"><strong>Detailed:</strong> {getFieldValue(data.long_description)}</p>
          </div>

          {/* Classification Section - MANDATORY FIELDS */}
          <div className="card-section classification-section">
            <h2>Industry Classification</h2>
            <div className="classification-grid">
              <div className="class-item">
                <label>Sector:</label>
                <span className="sector-tag">{getFieldValue(data.sector)}</span>
              </div>
              <div className="class-item">
                <label>Industry:</label>
                <span>{getFieldValue(data.industry)}</span>
              </div>
              <div className="class-item">
                <label>Sub-Industry:</label>
                <span>{getFieldValue(data.sub_industry)}</span>
              </div>
              <div className="class-item">
                <label>SIC Code:</label>
                <span className="sic-code">{getFieldValue(data.sic_code)}</span>
              </div>
              <div className="class-item full-width">
                <label>SIC Description:</label>
                <span>{getFieldValue(data.sic_text)}</span>
              </div>
            </div>

            {/* Tags */}
            {getFieldValue(data.tags) && getFieldValue(data.tags).length > 0 && (
              <div className="tags-container">
                <label>Tags:</label>
                <div className="tags">
                  {getFieldValue(data.tags).map((tag, idx) => (
                    <span key={idx} className="tag">{tag}</span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Company Details Section */}
          {(
            (getFieldValue(data.company_registration_number) && getFieldValue(data.company_registration_number) !== '-') ||
            (getFieldValue(data.vat_number) && getFieldValue(data.vat_number) !== '-')
          ) && (
              <div className="card-section details-section">
                <h2>Company Details</h2>
                <table className="details-table">
                  <tbody>
                    {getFieldValue(data.company_registration_number) && getFieldValue(data.company_registration_number) !== '-' && (
                      <tr>
                        <td className="label">Company Registration Number:</td>
                        <td>{getFieldValue(data.company_registration_number)}</td>
                      </tr>
                    )}
                    {getFieldValue(data.vat_number) && getFieldValue(data.vat_number) !== '-' && (
                      <tr>
                        <td className="label">VAT Number:</td>
                        <td>{getFieldValue(data.vat_number)}</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            )}

          {/* Contact Information Section */}
          {(
            (getFieldValue(data.full_address) && getFieldValue(data.full_address) !== '-') ||
            (getFieldValue(data.phone) && getFieldValue(data.phone) !== '-') ||
            (getFieldValue(data.sales_phone) && getFieldValue(data.sales_phone) !== '-') ||
            (getFieldValue(data.fax) && getFieldValue(data.fax) !== '-') ||
            (getFieldValue(data.mobile) && getFieldValue(data.mobile) !== '-') ||
            (getFieldValue(data.email) && getFieldValue(data.email) !== '-') ||
            (getFieldValue(data.all_emails) && getFieldValue(data.all_emails).length > 1) ||
            (getFieldValue(data.other_numbers) && getFieldValue(data.other_numbers).length > 0) ||
            (getFieldValue(data.hours_of_operation) && getFieldValue(data.hours_of_operation) !== '-')
          ) && (
              <div className="card-section contact-section">
                <h2>Contact Information</h2>
                <table className="details-table">
                  <tbody>
                    {getFieldValue(data.full_address) && getFieldValue(data.full_address) !== '-' && (
                      <tr>
                        <td className="label">Address:</td>
                        <td>{getFieldValue(data.full_address)}</td>
                      </tr>
                    )}
                    {getFieldValue(data.phone) && getFieldValue(data.phone) !== '-' && (
                      <tr>
                        <td className="label">Phone:</td>
                        <td>{getFieldValue(data.phone)}</td>
                      </tr>
                    )}
                    {getFieldValue(data.sales_phone) && getFieldValue(data.sales_phone) !== '-' && (
                      <tr>
                        <td className="label">Sales Phone:</td>
                        <td>{getFieldValue(data.sales_phone)}</td>
                      </tr>
                    )}
                    {getFieldValue(data.fax) && getFieldValue(data.fax) !== '-' && (
                      <tr>
                        <td className="label">Fax:</td>
                        <td>{getFieldValue(data.fax)}</td>
                      </tr>
                    )}
                    {getFieldValue(data.mobile) && getFieldValue(data.mobile) !== '-' && (
                      <tr>
                        <td className="label">Mobile:</td>
                        <td>{getFieldValue(data.mobile)}</td>
                      </tr>
                    )}
                    {getFieldValue(data.email) && getFieldValue(data.email) !== '-' && (
                      <tr>
                        <td className="label">Email:</td>
                        <td>
                          <a href={`mailto:${getFieldValue(data.email)}`}>{getFieldValue(data.email)}</a>
                        </td>
                      </tr>
                    )}
                    {getFieldValue(data.all_emails) && getFieldValue(data.all_emails).length > 1 && (
                      <tr>
                        <td className="label">Other Emails:</td>
                        <td>{getFieldValue(data.all_emails).slice(1).join(', ')}</td>
                      </tr>
                    )}
                    {getFieldValue(data.other_numbers) && getFieldValue(data.other_numbers).length > 0 && (
                      <tr>
                        <td className="label">Other Numbers:</td>
                        <td>{getFieldValue(data.other_numbers).join(', ')}</td>
                      </tr>
                    )}
                    {getFieldValue(data.hours_of_operation) && getFieldValue(data.hours_of_operation) !== '-' && (
                      <tr>
                        <td className="label">Hours of Operation:</td>
                        <td>{getFieldValue(data.hours_of_operation)}</td>
                      </tr>
                    )}
                    <tr>
                      <td className="label">HQ Location:</td>
                      <td>{getFieldValue(data.hq_indicator) ? 'Yes' : 'No'}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            )}

          {/* People Section */}
          {getFieldValue(data.people) && getFieldValue(data.people).length > 0 && getFieldValue(getFieldValue(data.people)[0].name) !== '-' && (
            <div className="card-section people-section">
              <h2>Team Members</h2>
              <table className="people-table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Title</th>
                    <th>Email</th>
                    <th>Profile URL</th>
                  </tr>
                </thead>
                <tbody>
                  {getFieldValue(data.people).map((person, idx) => (
                    <tr key={idx}>
                      <td>{getFieldValue(person.name)}</td>
                      <td>{getFieldValue(person.title)}</td>
                      <td>{getFieldValue(person.email) !== '-' ? <a href={`mailto:${getFieldValue(person.email)}`}>{getFieldValue(person.email)}</a> : '-'}</td>
                      <td>{getFieldValue(person.url) !== '-' ? <a href={getFieldValue(person.url)} target="_blank" rel="noopener noreferrer">View</a> : '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Certifications Section */}
          {getFieldValue(data.certifications) && getFieldValue(data.certifications).length > 0 && getFieldValue(data.certifications)[0] !== '-' && (
            <div className="card-section certifications-section">
              <h2>Certifications & Compliance</h2>
              <div className="certifications-grid">
                {getFieldValue(data.certifications).map((cert, idx) => (
                  <div key={idx} className="cert-badge">
                    {cert}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Services Section */}
          {getFieldValue(data.services) && getFieldValue(data.services).length > 0 && getFieldValue(getFieldValue(data.services)[0].service) !== '-' && (
            <div className="card-section services-section">
              <h2>Services & Solutions</h2>
              <table className="services-table">
                <thead>
                  <tr>
                    <th>Service</th>
                    <th>Type</th>
                  </tr>
                </thead>
                <tbody>
                  {getFieldValue(data.services).map((service, idx) => (
                    <tr key={idx}>
                      <td>{getFieldValue(service.service)}</td>
                      <td><span className={`service-type-badge ${getFieldValue(service.type).toLowerCase()}`}>{getFieldValue(service.type)}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Footer */}
          <div className="card-footer">
            <p className="extraction-info">
              Data extracted on {new Date(getFieldValue(data.extraction_timestamp)).toLocaleString()}
            </p>
            <p className="text-stats">
              Analyzed {getFieldValue(data.text_length)?.toLocaleString()} characters of content
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default EnhancedSummaryCard;
